import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from apps.organizations.models import Organization, OrganizationConfig
from apps.users.models import User, UserOrganizationRole, PasswordResetToken


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def org(db):
    org = Organization.objects.create(name='Test Club', slug='test-club')
    OrganizationConfig.objects.create(organization=org, allow_self_registration=True)
    return org


@pytest.fixture
def user(org):
    u = User(organization=org, email='alice@example.com', first_name='Alice', last_name='Smith')
    u.set_password('Str0ngPass!')
    u.save()
    UserOrganizationRole.objects.create(user=u, organization=org, role='member')
    return u


@pytest.mark.django_db
class TestPasswordResetRequest:
    def test_valid_email_generates_token(self, client, org, user):
        response = client.post(
            '/api/v1/auth/password/reset/',
            {'email': 'alice@example.com'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 200
        assert 'reset link' in response.json()['message']
        assert PasswordResetToken.objects.filter(user=user, is_used=False).count() == 1

    def test_unknown_email_returns_200(self, client, org):
        response = client.post(
            '/api/v1/auth/password/reset/',
            {'email': 'nobody@example.com'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 200
        assert 'reset link' in response.json()['message']
        assert PasswordResetToken.objects.count() == 0

    def test_second_request_invalidates_first_token(self, client, org, user):
        client.post(
            '/api/v1/auth/password/reset/',
            {'email': 'alice@example.com'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        first_token = PasswordResetToken.objects.get(user=user)
        assert not first_token.is_used

        client.post(
            '/api/v1/auth/password/reset/',
            {'email': 'alice@example.com'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        first_token.refresh_from_db()
        assert first_token.is_used
        assert PasswordResetToken.objects.filter(user=user, is_used=False).count() == 1

    def test_used_token_rejected(self, client, org, user):
        from datetime import timedelta
        token = PasswordResetToken.objects.create(
            user=user,
            is_used=True,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        response = client.post(
            '/api/v1/auth/password/reset/confirm/',
            {'token': str(token.token), 'password': 'NewStr0ng!'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 400
        assert 'already been used' in response.json()['detail']

    def test_expired_token_returns_410(self, client, org, user):
        token = PasswordResetToken.objects.create(
            user=user,
            is_used=False,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        response = client.post(
            '/api/v1/auth/password/reset/confirm/',
            {'token': str(token.token), 'password': 'NewStr0ng!'},
            format='json',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 410
        assert 'expired' in response.json()['detail']
