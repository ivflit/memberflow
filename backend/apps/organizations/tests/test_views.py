import pytest
from rest_framework.test import APIClient
from apps.organizations.models import Organization


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def org(db):
    return Organization.objects.create(name='Test Club', slug='test-club')


@pytest.mark.django_db
class TestHealthCheckView:
    def test_returns_200_with_tenant_slug(self, client, org):
        response = client.get(
            '/api/v1/health/',
            HTTP_X_TENANT_SLUG='test-club',
        )
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'tenant': 'test-club'}

    def test_returns_404_for_unknown_org(self, client):
        response = client.get(
            '/api/v1/health/',
            HTTP_X_TENANT_SLUG='no-such-org',
        )
        assert response.status_code == 404
        assert response.json() == {'error': 'Organisation not found'}

    def test_returns_400_with_no_tenant_header(self, client):
        response = client.get('/api/v1/health/')
        assert response.status_code == 400
        assert response.json() == {'error': 'Tenant not specified'}
