import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password
from django.utils import timezone
from datetime import timedelta
from apps.core.models import TenantAwareModel


class User(TenantAwareModel):
    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=128)
    date_of_birth = models.DateField(null=True, blank=True)
    address_street = models.CharField(max_length=255, null=True, blank=True)
    address_city = models.CharField(max_length=100, null=True, blank=True)
    address_postcode = models.CharField(max_length=20, null=True, blank=True)
    address_country = models.CharField(max_length=100, null=True, blank=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'email'],
                name='unique_email_per_org',
            )
        ]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return django_check_password(raw_password, self.password)

    def __str__(self):
        return f'{self.email} ({self.organization})'


class UserOrganizationRole(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('org_staff', 'Org Staff'),
        ('org_admin', 'Org Admin'),
        ('platform_admin', 'Platform Admin'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='user_roles',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f'{self.user.email} - {self.role} @ {self.organization}'


class UserInvitation(TenantAwareModel):
    email = models.EmailField()
    token = models.UUIDField(unique=True, default=uuid.uuid4)
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations',
    )
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Invitation for {self.email} ({self.organization})'


class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.UUIDField(unique=True, default=uuid.uuid4)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Reset token for {self.user.email}'


class BlacklistedRefreshToken(models.Model):
    """Lightweight blacklist for refresh tokens — keyed by JTI."""
    jti = models.CharField(max_length=255, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['jti'])]

    def __str__(self):
        return f'Blacklisted JTI: {self.jti}'
