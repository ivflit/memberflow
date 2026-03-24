from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from apps.users.models import User


class TenantJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that looks up our User model (not Django's auth.User).
    Also checks our custom BlacklistedRefreshToken store.
    """

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise InvalidToken('No user matching this token was found')

        if not user.is_active:
            raise InvalidToken('User is inactive')

        return user
