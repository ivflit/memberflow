import pytest
from django.db import IntegrityError
from apps.organizations.models import Organization


@pytest.mark.django_db
class TestOrganizationModel:
    def test_creates_with_uuid_pk(self):
        org = Organization.objects.create(name='Test Club', slug='test-club')
        assert org.pk is not None
        assert str(org.pk)  # UUID is stringifiable

    def test_str_returns_name(self):
        org = Organization.objects.create(name='Springfield CC', slug='springfield-cc')
        assert str(org) == 'Springfield CC'

    def test_slug_is_unique(self):
        Organization.objects.create(name='Club A', slug='my-club')
        with pytest.raises(IntegrityError):
            Organization.objects.create(name='Club B', slug='my-club')

    def test_is_active_defaults_to_true(self):
        org = Organization.objects.create(name='Test', slug='test')
        assert org.is_active is True
