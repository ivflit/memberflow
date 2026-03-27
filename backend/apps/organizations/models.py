import uuid
from django.db import models


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OrganizationConfig(models.Model):
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='config',
    )
    allow_self_registration = models.BooleanField(default=False)
    # Branding: {"primary_color": "#3273dc", "secondary_color": "#23d160", "logo_url": "https://..."}
    branding = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'Config for {self.organization}'
