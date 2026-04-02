"""Unit tests for DOB and address fields on the User profile API."""
import datetime
import pytest
from apps.organizations.models import Organization, OrganizationConfig
from apps.users.models import User, UserOrganizationRole
from apps.users.serializers import ProfileUpdateSerializer, RegisterSerializer
from apps.users.tokens import make_tokens_for_user


@pytest.fixture
def org(db):
    org = Organization.objects.create(name='Test Club DOB', slug='test-club-dob')
    OrganizationConfig.objects.create(organization=org)
    return org


@pytest.fixture
def user(org):
    u = User(organization=org, email='dob@test.com', first_name='D', last_name='O')
    u.set_password('TestPass123!')
    u.save()
    UserOrganizationRole.objects.create(user=u, organization=org, role='member')
    return u


@pytest.fixture
def auth_headers(user):
    access, _ = make_tokens_for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {access}'}


class TestProfileUpdateSerializerValidation:
    def test_future_dob_rejected(self):
        s = ProfileUpdateSerializer(data={'date_of_birth': '2099-01-01'})
        assert not s.is_valid()
        assert 'date_of_birth' in s.errors

    def test_past_dob_accepted(self):
        s = ProfileUpdateSerializer(data={'date_of_birth': '1990-06-15'})
        assert s.is_valid(), s.errors

    def test_empty_string_dob_coerced_to_none(self):
        s = ProfileUpdateSerializer(data={'date_of_birth': ''})
        assert s.is_valid(), s.errors
        assert s.validated_data['date_of_birth'] is None

    def test_null_dob_accepted(self):
        s = ProfileUpdateSerializer(data={'date_of_birth': None})
        assert s.is_valid(), s.errors
        assert s.validated_data['date_of_birth'] is None

    def test_empty_string_address_coerced_to_none(self):
        s = ProfileUpdateSerializer(data={'address_street': '', 'address_city': ''})
        assert s.is_valid(), s.errors
        assert s.validated_data['address_street'] is None
        assert s.validated_data['address_city'] is None


class TestRegisterSerializerDobAddress:
    def test_register_with_dob_and_address(self):
        s = RegisterSerializer(data={
            'email': 'reg@test.com', 'password': 'TestPass123!',
            'first_name': 'R', 'last_name': 'G',
            'date_of_birth': '1985-03-20',
            'address_street': '1 Test St', 'address_city': 'Manchester',
            'address_postcode': 'M1 1AA', 'address_country': 'UK',
        })
        assert s.is_valid(), s.errors

    def test_register_without_optional_fields(self):
        s = RegisterSerializer(data={
            'email': 'reg2@test.com', 'password': 'TestPass123!',
            'first_name': 'R', 'last_name': 'G',
        })
        assert s.is_valid(), s.errors

    def test_register_future_dob_rejected(self):
        s = RegisterSerializer(data={
            'email': 'reg3@test.com', 'password': 'TestPass123!',
            'first_name': 'R', 'last_name': 'G',
            'date_of_birth': '2099-01-01',
        })
        assert not s.is_valid()
        assert 'date_of_birth' in s.errors


class TestAgeCalculation:
    def test_age_calculated_correctly(self, org):
        from apps.admin_portal.serializers import _calculate_age
        dob = datetime.date(1990, 1, 1)
        age = _calculate_age(dob)
        today = datetime.date.today()
        expected = today.year - 1990 - ((today.month, today.day) < (1, 1))
        assert age == expected

    def test_age_none_when_dob_null(self):
        from apps.admin_portal.serializers import _calculate_age
        assert _calculate_age(None) is None


class TestProfileApiTenantIsolation:
    @pytest.mark.django_db
    def test_member_cannot_read_other_org_member_via_profile(self, client, org, user, auth_headers):
        """GET /api/v1/profile/ returns only the authenticated user's own data."""
        org2 = Organization.objects.create(name='Other Club', slug='other-club-dob')
        OrganizationConfig.objects.create(organization=org2)
        other = User(organization=org2, email='other@other.com', first_name='X', last_name='Y')
        other.set_password('TestPass123!')
        other.save()

        # Our user's profile should not expose other org's user
        response = client.get(
            '/api/v1/profile/',
            HTTP_HOST='test-club-dob.localhost',
            **auth_headers,
        )
        assert response.status_code == 200
        assert response.json()['email'] == 'dob@test.com'
