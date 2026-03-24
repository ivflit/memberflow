import pytest


@pytest.fixture(autouse=True)
def enable_debug(settings):
    """Ensure DEBUG=True so X-Tenant-Slug header is read by TenantMiddleware in all tests."""
    settings.DEBUG = True
