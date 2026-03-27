import pytest
from django.test import RequestFactory
from unittest.mock import patch, MagicMock
from apps.core.middleware import TenantMiddleware
from apps.organizations.models import Organization


@pytest.fixture
def get_response():
    return MagicMock(return_value=MagicMock(status_code=200))


@pytest.fixture
def middleware(get_response):
    return TenantMiddleware(get_response)


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.mark.django_db
class TestTenantMiddlewareHeaderResolution:
    def test_resolves_slug_from_header_in_debug_mode(self, middleware, factory, settings):
        settings.DEBUG = True
        org = Organization.objects.create(name='Test Club', slug='test-club')
        request = factory.get('/', HTTP_X_TENANT_SLUG='test-club', SERVER_NAME='localhost')
        middleware(request)
        assert request.tenant == org

    def test_header_ignored_in_production_mode(self, middleware, factory, settings):
        settings.DEBUG = False
        Organization.objects.create(name='Test Club', slug='test-club')
        # In production, subdomain is used — localhost has no subdomain so slug is None
        # Root domain pass-through: request.tenant = None, continues to view
        request = factory.get('/', HTTP_X_TENANT_SLUG='test-club', SERVER_NAME='localhost')
        middleware(request)
        assert request.tenant is None

    def test_falls_back_to_subdomain_when_no_header(self, middleware, factory, settings):
        settings.DEBUG = True
        org = Organization.objects.create(name='Test Club', slug='test-club')
        request = factory.get('/', SERVER_NAME='test-club.memberflow.com')
        middleware(request)
        assert request.tenant == org


@pytest.mark.django_db
class TestTenantMiddlewareRejection:
    def test_returns_404_for_unknown_slug(self, middleware, factory, settings):
        settings.DEBUG = True
        request = factory.get('/', HTTP_X_TENANT_SLUG='no-such-club')
        response = middleware(request)
        assert response.status_code == 404

    def test_returns_404_for_inactive_org(self, middleware, factory, settings):
        settings.DEBUG = True
        Organization.objects.create(name='Inactive Club', slug='inactive-club', is_active=False)
        request = factory.get('/', HTTP_X_TENANT_SLUG='inactive-club')
        response = middleware(request)
        assert response.status_code == 404

    def test_passes_through_with_null_tenant_when_no_slug_resolvable(self, middleware, factory, settings):
        settings.DEBUG = True
        # No header, no subdomain (plain 'localhost') → root/platform domain
        # Middleware sets request.tenant = None and passes through
        request = factory.get('/', SERVER_NAME='localhost')
        middleware(request)
        assert request.tenant is None
