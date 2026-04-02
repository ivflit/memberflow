from django.db import models
from apps.core.models import TenantAwareModel


class MembershipTier(TenantAwareModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.organization})'


class Membership(TenantAwareModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    tier = models.ForeignKey(
        MembershipTier,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'user'],
                name='unique_membership_per_org',
            )
        ]

    def __str__(self):
        return f'{self.user} — {self.tier} ({self.status})'
