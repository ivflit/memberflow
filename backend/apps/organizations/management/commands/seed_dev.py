from django.core.management.base import BaseCommand
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Seed development database with a test organisation'

    def handle(self, *args, **options):
        _, created = Organization.objects.get_or_create(
            slug='test-club',
            defaults={
                'name': 'Test Club',
                'is_active': True,
            },
        )
        if created:
            self.stdout.write('[seed_dev] Organisation "test-club" created.')
        else:
            self.stdout.write('[seed_dev] Organisation "test-club" ready.')
