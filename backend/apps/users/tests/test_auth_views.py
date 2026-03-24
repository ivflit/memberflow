import pytest
from rest_framework.test import APIClient
from apps.organizations.models import Organization, OrganizationConfig
from apps.users.models import User, UserOrganizationRole


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def org(db):
    org = Organization.objects.create(name='Test Club', slug='test-club')
    OrganizationConfig.objects.create(organization=org, allow_self_registration=True)
    return org


@pytest.fixture
def org_no_reg(db):
    org = Organization.objects.create(name='Closed Club', slug='closed-club')
    OrganizationConfig.objects.create(organization=org, allow_self_registration=False)
    return org


@pytest.fixture
def registered_user(org):
    u = User(organization=org, email='alice@example.com', first_name='Alice', last_name='Smith')
    u.set_password('Str0ngPass!')
    u.save()
    UserOrganizationRole.objects.create(user=u, organization=org, role='member')
    return u


@pytest.mark.django_db
class TestRegisterView:
    def test_register_success(self, client, org):
        response = client.post(
            '/api/v1/auth/register/',
            {
                'email': 'newuser@example.com',
                'password': 'Str0ngPass!',
                'first_name': 'New',
                'last_name': 'User',
            },
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 201
        data = response.json()
        assert 'access' in data
        assert 'refresh' in data
        assert data['user']['role'] == 'member'
        assert data['user']['email'] == 'newuser@example.com'

    def test_register_forbidden_when_self_registration_disabled(self, client, org_no_reg):
        response = client.post(
            '/api/v1/auth/register/',
            {
                'email': 'newuser@example.com',
                'password': 'Str0ngPass!',
                'first_name': 'New',
                'last_name': 'User',
            },
            format='json',
            HTTP_X_TENANT_SLUG='closed-club',
        )
        assert response.status_code == 403

    def test_register_conflict_on_duplicate_email(self, client, org, registered_user):
        response = client.post(
            '/api/v1/auth/register/',
            {
                'email': 'alice@example.com',
                'password': 'Str0ngPass!',
                'first_name': 'Alice',
                'last_name': 'Smith',
            },
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 409

    def test_register_bad_password(self, client, org):
        response = client.post(
            '/api/v1/auth/register/',
            {
                'email': 'newuser@example.com',
                'password': '123',
                'first_name': 'New',
                'last_name': 'User',
            },
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, client, org, registered_user):
        response = client.post(
            '/api/v1/auth/login/',
            {'email': 'alice@example.com', 'password': 'Str0ngPass!'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 200
        data = response.json()
        assert 'access' in data
        assert 'refresh' in data
        assert data['user']['email'] == 'alice@example.com'

    def test_login_wrong_password(self, client, org, registered_user):
        response = client.post(
            '/api/v1/auth/login/',
            {'email': 'alice@example.com', 'password': 'wrongpassword'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid email or password.'

    def test_login_wrong_email(self, client, org, registered_user):
        response = client.post(
            '/api/v1/auth/login/',
            {'email': 'nobody@example.com', 'password': 'Str0ngPass!'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid email or password.'

    def test_login_inactive_user(self, client, org, registered_user):
        registered_user.is_active = False
        registered_user.save()
        response = client.post(
            '/api/v1/auth/login/',
            {'email': 'alice@example.com', 'password': 'Str0ngPass!'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 403
        assert response.json()['detail'] == 'Account is inactive.'


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_success(self, client, org, registered_user):
        # Login first to get tokens
        login_resp = client.post(
            '/api/v1/auth/login/',
            {'email': 'alice@example.com', 'password': 'Str0ngPass!'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        refresh_token = login_resp.json()['refresh']

        # Logout
        response = client.post(
            '/api/v1/auth/logout/',
            {'refresh': refresh_token},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 204

    def test_logout_missing_token(self, client, org):
        response = client.post(
            '/api/v1/auth/logout/',
            {},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 400

    def test_logout_already_blacklisted(self, client, org, registered_user):
        login_resp = client.post(
            '/api/v1/auth/login/',
            {'email': 'alice@example.com', 'password': 'Str0ngPass!'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        refresh_token = login_resp.json()['refresh']

        client.post(
            '/api/v1/auth/logout/',
            {'refresh': refresh_token},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        # Second logout should return 400
        response = client.post(
            '/api/v1/auth/logout/',
            {'refresh': refresh_token},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 400
