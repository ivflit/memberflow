"""E2E-style backend tests for admin and platform member API endpoints."""
import datetime
import csv
import io
import pytest
from apps.organizations.models import Organization, OrganizationConfig
from apps.users.models import User, UserOrganizationRole
from apps.users.tokens import make_tokens_for_user


@pytest.fixture
def org_a(db):
    org = Organization.objects.create(name='Club A', slug='club-a-admin')
    OrganizationConfig.objects.create(organization=org)
    return org


@pytest.fixture
def org_b(db):
    org = Organization.objects.create(name='Club B', slug='club-b-admin')
    OrganizationConfig.objects.create(organization=org)
    return org


def make_user(org, email, role='member', dob=None, city=None):
    u = User(
        organization=org, email=email, first_name='Test', last_name='User',
        date_of_birth=dob, address_city=city,
    )
    u.set_password('TestPass123!')
    u.save()
    UserOrganizationRole.objects.create(user=u, organization=org, role=role)
    return u


def auth_header(user):
    access, _ = make_tokens_for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {access}'}


class TestAdminMemberList:
    def test_list_contains_age_not_raw_dob(self, client, org_a):
        admin = make_user(org_a, 'admin@a.com', role='org_admin')
        make_user(org_a, 'member@a.com', dob=datetime.date(1990, 5, 10))
        response = client.get(
            '/api/v1/admin/members/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 200
        rows = response.json()
        member_row = next(r for r in rows if r['email'] == 'member@a.com')
        assert 'age' in member_row
        assert isinstance(member_row['age'], int)
        assert 'date_of_birth' not in member_row
        assert 'address_city' not in member_row

    def test_staff_can_access_list(self, client, org_a):
        staff = make_user(org_a, 'staff@a.com', role='org_staff')
        response = client.get(
            '/api/v1/admin/members/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(staff),
        )
        assert response.status_code == 200

    def test_member_cannot_access_list(self, client, org_a):
        member = make_user(org_a, 'plain@a.com', role='member')
        response = client.get(
            '/api/v1/admin/members/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(member),
        )
        assert response.status_code == 403

    def test_tenant_isolation_list(self, client, org_a, org_b):
        """Org A admin cannot see org B members in the list."""
        admin_a = make_user(org_a, 'admin2@a.com', role='org_admin')
        make_user(org_b, 'member@b.com')
        response = client.get(
            '/api/v1/admin/members/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(admin_a),
        )
        assert response.status_code == 200
        emails = [r['email'] for r in response.json()]
        assert 'member@b.com' not in emails


class TestAdminMemberDetail:
    def test_detail_has_dob_and_address(self, client, org_a):
        admin = make_user(org_a, 'admin3@a.com', role='org_admin')
        member = make_user(org_a, 'detail@a.com',
                           dob=datetime.date(1985, 3, 20), city='Bristol')
        response = client.get(
            f'/api/v1/admin/members/{member.id}/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 200
        data = response.json()
        assert data['date_of_birth'] == '1985-03-20'
        assert data['address_city'] == 'Bristol'
        assert 'age' in data

    def test_cross_tenant_detail_returns_404(self, client, org_a, org_b):
        """Org A admin cannot fetch org B member detail."""
        admin_a = make_user(org_a, 'admin4@a.com', role='org_admin')
        member_b = make_user(org_b, 'secret@b.com')
        response = client.get(
            f'/api/v1/admin/members/{member_b.id}/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(admin_a),
        )
        assert response.status_code == 404


class TestMemberExport:
    def test_export_contains_dob_and_address_columns(self, client, org_a):
        admin = make_user(org_a, 'admin5@a.com', role='org_admin')
        make_user(org_a, 'export@a.com', dob=datetime.date(1992, 7, 4), city='Leeds')
        response = client.get(
            '/api/v1/admin/members/export/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']
        content = response.content.decode()
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        export_row = next(r for r in rows if r['email'] == 'export@a.com')
        assert export_row['date_of_birth'] == '1992-07-04'
        assert export_row['address_city'] == 'Leeds'

    def test_staff_cannot_export(self, client, org_a):
        staff = make_user(org_a, 'staff2@a.com', role='org_staff')
        response = client.get(
            '/api/v1/admin/members/export/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(staff),
        )
        assert response.status_code == 403

    def test_export_tenant_isolation(self, client, org_a, org_b):
        """Export for org A should not include org B members."""
        admin_a = make_user(org_a, 'admin6@a.com', role='org_admin')
        make_user(org_b, 'secret2@b.com')
        response = client.get(
            '/api/v1/admin/members/export/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(admin_a),
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert 'secret2@b.com' not in content


class TestPlatformAdmin:
    def test_platform_admin_can_read_cross_tenant(self, client, org_a, org_b):
        platform_admin = make_user(org_a, 'platform@a.com', role='platform_admin')
        member_b = make_user(org_b, 'cross@b.com', dob=datetime.date(1988, 11, 30))
        response = client.get(
            f'/api/v1/platform/members/{member_b.id}/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(platform_admin),
        )
        assert response.status_code == 200
        assert response.json()['email'] == 'cross@b.com'

    def test_platform_admin_can_patch_dob(self, client, org_a, org_b):
        platform_admin = make_user(org_a, 'platform2@a.com', role='platform_admin')
        member_b = make_user(org_b, 'patch@b.com')
        response = client.patch(
            f'/api/v1/platform/members/{member_b.id}/',
            data='{"date_of_birth": "1975-08-12"}',
            content_type='application/json',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(platform_admin),
        )
        assert response.status_code == 200
        assert response.json()['date_of_birth'] == '1975-08-12'

    def test_org_admin_cannot_access_platform_endpoint(self, client, org_a, org_b):
        org_admin = make_user(org_a, 'orgadmin2@a.com', role='org_admin')
        member_b = make_user(org_b, 'protected@b.com')
        response = client.get(
            f'/api/v1/platform/members/{member_b.id}/',
            HTTP_HOST='club-a-admin.localhost',
            **auth_header(org_admin),
        )
        assert response.status_code == 403
