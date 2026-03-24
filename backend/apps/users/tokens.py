import uuid
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, Token
from rest_framework_simplejwt.settings import api_settings


def make_tokens_for_user(user):
    """
    Issue an access + refresh token pair for our custom User model.
    Does NOT use simplejwt's for_user() because that requires Django's auth.User.
    The refresh token is still blacklistable via its JTI.
    """
    from apps.users.models import UserOrganizationRole

    try:
        role_obj = UserOrganizationRole.objects.get(
            user=user, organization_id=user.organization_id
        )
        role = role_obj.role
    except UserOrganizationRole.DoesNotExist:
        role = 'member'

    # Build refresh token manually
    refresh = RefreshToken()
    refresh[api_settings.USER_ID_CLAIM] = str(user.pk)
    refresh['organization_id'] = str(user.organization_id)
    refresh['role'] = role

    # Build access token from refresh
    access = refresh.access_token
    access[api_settings.USER_ID_CLAIM] = str(user.pk)
    access['organization_id'] = str(user.organization_id)
    access['role'] = role

    return access, refresh
