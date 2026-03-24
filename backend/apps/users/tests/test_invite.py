import uuid
import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from apps.organizations.models import Organization, OrganizationConfig
from apps.users.models import User, UserOrganizationRole, UserInvitation


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def org(db):
    org = Organization.objects.create(name='Test Club', slug='test-club')
    OrganizationConfig.objects.create(organization=org, allow_self_registration=True)
    return org


@pytest.fixture
def org2(db):
    org = Organization.objects.create(name='Other Club', slug='other-club')
    OrganizationConfig.objects.create(organization=org, allow_self_registration=False)
    return org


@pytest.fixture
def admin_user(org):
    u = User(organization=org, email='admin@example.com', first_name='Admin', last_name='User')
    u.set_password('Str0ngPass!')
    u.save()
    UserOrganizationRole.objects.create(user=u, organization=org, role='org_admin')
    return u


@pytest.mark.django_db
class TestInviteAccept:
    def test_used_invite_token_returns_400(self, client, org, admin_user):
        invitation = UserInvitation.objects.create(
            organization=org,
            email='bob@example.com',
            invited_by=admin_user,
            is_used=True,
            expires_at=timezone.now() + timedelta(days=7),
        )
        response = client.post(
            '/api/v1/auth/invite/accept/',
            {
                'token': str(invitation.token),
                'password': 'Str0ngPass!',
                'first_name': 'Bob',
                'last_name': 'Smith',
            },
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 400
        assert 'already been used' in response.json()['detail']

    def test_expired_invite_returns_410(self, client, org, admin_user):
        invitation = UserInvitation.objects.create(
            organization=org,
            email='bob@example.com',
            invited_by=admin_user,
            is_used=False,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        response = client.post(
            '/api/v1/auth/invite/accept/',
            {
                'token': str(invitation.token),
                'password': 'Str0ngPass!',
                'first_name': 'Bob',
                'last_name': 'Smith',
            },
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 410
        assert 'expired' in response.json()['detail']

    def test_cross_org_invite_token_rejected_on_wrong_subdomain(
        self, client, org, org2, admin_user
    ):
        # Invitation created for org but submitted with org2's slug
        invitation = UserInvitation.objects.create(
            organization=org,
            email='bob@example.com',
            invited_by=admin_user,
            is_used=False,
            expires_at=timezone.now() + timedelta(days=7),
        )
        response = client.post(
            '/api/v1/auth/invite/accept/',
            {
                'token': str(invitation.token),
                'password': 'Str0ngPass!',
                'first_name': 'Bob',
                'last_name': 'Smith',
            },
            format='json',
            HTTP_X_TENANT_SLUG='other-club',
        )
        assert response.status_code == 400
