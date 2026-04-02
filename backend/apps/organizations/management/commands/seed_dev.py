from django.core.management.base import BaseCommand
from apps.organizations.models import Organization, OrganizationConfig
from apps.users.models import User, UserOrganizationRole

DEV_USERS = [
    {'email': 'member@dev.local', 'first_name': 'Dev', 'last_name': 'Member', 'role': 'member'},
    {'email': 'staff@dev.local', 'first_name': 'Dev', 'last_name': 'Staff', 'role': 'org_staff'},
    {'email': 'admin@dev.local', 'first_name': 'Dev', 'last_name': 'Admin', 'role': 'org_admin'},
]
DEV_PASSWORD = 'devpass123'


class Command(BaseCommand):
    help = 'Seed development database with a test organisation and dev users'

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

        for spec in DEV_USERS:
            user, u_created = User.objects.get_or_create(
                organization=org,
                email=spec['email'],
                defaults={
                    'first_name': spec['first_name'],
                    'last_name': spec['last_name'],
                    'is_active': True,
                },
            )
            if u_created:
                user.set_password(DEV_PASSWORD)
                user.save()
            UserOrganizationRole.objects.get_or_create(
                user=user,
                organization=org,
                defaults={'role': spec['role']},
            )
            status = 'created' if u_created else 'ready'
            self.stdout.write(f'[seed_dev] {spec["role"]} user {spec["email"]} {status}.')
