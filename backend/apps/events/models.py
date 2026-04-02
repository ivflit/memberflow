from django.contrib.postgres.fields import ArrayField
from django.db import models
from apps.core.models import TenantAwareModel


class EventCategory(TenantAwareModel):
    name = models.CharField(max_length=50)
    colour = models.CharField(max_length=7, null=True, blank=True)

    class Meta:
        unique_together = ('organization', 'name')

    def __str__(self):
        return f'{self.name} ({self.organization})'


class Event(TenantAwareModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    venue_name = models.CharField(max_length=200, null=True, blank=True)
    venue_postcode = models.CharField(max_length=20, null=True, blank=True)
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
    )
    image_url = models.URLField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    restricted_to_tiers = models.ManyToManyField(
        'memberships.MembershipTier',
        blank=True,
        related_name='events',
    )
    restricted_to_roles = ArrayField(
        models.CharField(max_length=20),
        blank=True,
        default=list,
    )

    class Meta:
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'start_datetime']),
        ]

    def __str__(self):
        return f'{self.title} ({self.status}) @ {self.organization}'
