from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from apps.core.throttles import LoginRateThrottle, PasswordResetRateThrottle
from apps.core.permissions import IsOrgStaff
from apps.users.models import (
    User, UserOrganizationRole, UserInvitation, PasswordResetToken, BlacklistedRefreshToken
)
from apps.users.serializers import (
    RegisterSerializer, LoginSerializer, SendInviteSerializer,
    InviteAcceptSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserSerializer,
)
from apps.users.tokens import make_tokens_for_user


def _token_response(user):
    """Issue access + refresh tokens for a user."""
    access, refresh = make_tokens_for_user(user)
    role = access.get('role', 'member')

    return {
        'access': str(access),
        'refresh': str(refresh),
        'user': {
            'id': str(user.pk),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role,
        },
    }


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Check self-registration flag
        try:
            config = request.tenant.config
        except Exception:
            config = None

        if not config or not config.allow_self_registration:
            return Response(
                {'detail': 'Self-registration is not enabled for this organisation.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email = data['email']

        # Check email uniqueness within tenant
        if User.objects.for_tenant(request.tenant).filter(email=email).exists():
            return Response(
                {'detail': 'A user with this email already exists in this organisation.'},
                status=status.HTTP_409_CONFLICT,
            )

        user = User(
            organization=request.tenant,
            email=email,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        user.set_password(data['password'])
        user.save()

        UserOrganizationRole.objects.create(
            user=user,
            organization=request.tenant,
            role='member',
        )

        return Response(_token_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email = data['email']
        password = data['password']

        try:
            user = User.objects.for_tenant(request.tenant).get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'detail': 'Account is inactive.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(_token_response(user), status=status.HTTP_200_OK)


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = SimpleJWTRefreshToken(refresh_token)
            jti = token['jti']
        except (TokenError, KeyError) as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if BlacklistedRefreshToken.objects.filter(jti=jti).exists():
            return Response(
                {'detail': 'Token is already blacklisted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        BlacklistedRefreshToken.objects.create(jti=jti)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantTokenRefreshView(BaseTokenRefreshView):
    """Refresh view that checks our custom blacklist."""

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        refresh_token_str = request.data.get('refresh')
        if refresh_token_str:
            try:
                token = SimpleJWTRefreshToken(refresh_token_str)
                jti = token.get('jti')
                if jti and BlacklistedRefreshToken.objects.filter(jti=jti).exists():
                    raise InvalidToken('Token is blacklisted.')
            except TokenError:
                pass  # Let the parent handle invalid tokens
        return super().post(request, *args, **kwargs)


class SendInviteView(APIView):
    permission_classes = [IsOrgStaff]

    def post(self, request):
        serializer = SendInviteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        if User.objects.for_tenant(request.tenant).filter(email=email).exists():
            return Response(
                {'detail': 'A user with this email already exists in this organisation.'},
                status=status.HTTP_409_CONFLICT,
            )

        invitation = UserInvitation.objects.create(
            organization=request.tenant,
            email=email,
            invited_by=request.user,
        )

        # Build base_url for email link
        scheme = request.scheme
        base_url = f'{scheme}://{request.tenant.slug}.localhost:5173'

        try:
            from tasks.email import send_invite_email
            send_invite_email.delay(str(invitation.pk), base_url)
        except Exception:
            # Celery may not be running in dev; log but don't fail
            pass

        return Response({'message': 'Invitation sent'}, status=status.HTTP_201_CREATED)


class InviteAcceptView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = InviteAcceptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        token_value = data['token']

        try:
            invitation = UserInvitation.objects.select_related('organization').get(
                token=token_value,
                organization=request.tenant,
            )
        except UserInvitation.DoesNotExist:
            return Response(
                {'detail': 'Invalid or unknown invitation token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invitation.is_used:
            return Response(
                {'detail': 'This invitation has already been used.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invitation.expires_at < timezone.now():
            return Response(
                {'detail': 'This invitation has expired.'},
                status=status.HTTP_410_GONE,
            )

        user = User(
            organization=request.tenant,
            email=invitation.email,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        user.set_password(data['password'])
        user.save()

        UserOrganizationRole.objects.create(
            user=user,
            organization=request.tenant,
            role='member',
        )

        invitation.is_used = True
        invitation.save()

        return Response(_token_response(user), status=status.HTTP_201_CREATED)


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        message = {'message': 'If that email is registered, a reset link has been sent.'}

        try:
            user = User.objects.for_tenant(request.tenant).get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response(message, status=status.HTTP_200_OK)

        # Invalidate any existing unused reset tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        # Create new token
        from datetime import timedelta
        reset_token = PasswordResetToken(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        reset_token.save()

        scheme = request.scheme
        base_url = f'{scheme}://{request.tenant.slug}.localhost:5173'

        try:
            from tasks.email import send_reset_email
            send_reset_email.delay(str(reset_token.pk), base_url)
        except Exception:
            pass

        return Response(message, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        token_value = data['token']

        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=token_value,
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'detail': 'This reset link has already been used or is invalid.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reset_token.is_used:
            return Response(
                {'detail': 'This reset link has already been used or is invalid.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reset_token.expires_at < timezone.now():
            return Response(
                {'detail': 'This reset link has expired.'},
                status=status.HTTP_410_GONE,
            )

        user = reset_token.user
        user.set_password(data['password'])
        user.save()

        reset_token.is_used = True
        reset_token.save()

        return Response(_token_response(user), status=status.HTTP_200_OK)
