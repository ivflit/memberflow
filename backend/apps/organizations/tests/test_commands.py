import pytest
from django.core.management import call_command
from apps.organizations.models import Organization


@pytest.mark.django_db
class TestSeedDevCommand:
    def test_creates_test_club_org(self):
        assert not Organization.objects.filter(slug='test-club').exists()
        call_command('seed_dev')
        assert Organization.objects.filter(slug='test-club').exists()

    def test_created_org_has_correct_fields(self):
        call_command('seed_dev')
        org = Organization.objects.get(slug='test-club')
        assert org.name == 'Test Club'
        assert org.is_active is True

    def test_idempotent_does_not_create_duplicate(self):
        call_command('seed_dev')
        call_command('seed_dev')
        assert Organization.objects.filter(slug='test-club').count() == 1

    def test_idempotent_does_not_raise(self):
        call_command('seed_dev')
        # Should not raise any exception
        call_command('seed_dev')
