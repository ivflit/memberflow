from django.core.management.base import BaseCommand
from apps.organizations.models import Organization, OrganizationConfig


class Command(BaseCommand):
    help = 'Seed development database with a test organisation'

    def handle(self, *args, **options):
        org, created = Organization.objects.get_or_create(
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

        config, config_created = OrganizationConfig.objects.get_or_create(
            organization=org,
            defaults={'allow_self_registration': True},
        )
        if not config_created and not config.allow_self_registration:
            config.allow_self_registration = True
            config.save()
        self.stdout.write('[seed_dev] OrganizationConfig allow_self_registration=True set.')
