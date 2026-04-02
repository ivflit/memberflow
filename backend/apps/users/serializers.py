from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers
from apps.users.models import User, UserOrganizationRole


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'date_of_birth', 'address_street', 'address_city',
            'address_postcode', 'address_country',
        ]

    def get_role(self, obj):
        try:
            role_obj = UserOrganizationRole.objects.get(
                user=obj, organization_id=obj.organization_id
            )
            return role_obj.role
        except UserOrganizationRole.DoesNotExist:
            return 'member'


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address_street = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    address_city = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    address_postcode = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    address_country = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_date_of_birth(self, value):
        if value is not None and value > timezone.now().date():
            raise serializers.ValidationError('Date of birth cannot be in the future.')
        return value

    def to_internal_value(self, data):
        mutable = data.copy() if hasattr(data, 'copy') else dict(data)
        for field in ('address_street', 'address_city', 'address_postcode', 'address_country'):
            if mutable.get(field) == '':
                mutable[field] = None
        if mutable.get('date_of_birth') == '':
            mutable['date_of_birth'] = None
        return super().to_internal_value(mutable)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class InviteAcceptSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address_street = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    address_city = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    address_postcode = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    address_country = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_date_of_birth(self, value):
        if value is not None and value > timezone.now().date():
            raise serializers.ValidationError('Date of birth cannot be in the future.')
        return value

    def to_internal_value(self, data):
        mutable = data.copy() if hasattr(data, 'copy') else dict(data)
        for field in ('address_street', 'address_city', 'address_postcode', 'address_country'):
            if mutable.get(field) == '':
                mutable[field] = None
        if mutable.get('date_of_birth') == '':
            mutable['date_of_birth'] = None
        return super().to_internal_value(mutable)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value


class SendInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address_street = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    address_city = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    address_postcode = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    address_country = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)

    def validate_date_of_birth(self, value):
        if value is not None and value > timezone.now().date():
            raise serializers.ValidationError('Date of birth cannot be in the future.')
        return value

    def to_internal_value(self, data):
        # Coerce empty strings to None for address fields and date_of_birth
        mutable = data.copy() if hasattr(data, 'copy') else dict(data)
        for field in ('address_street', 'address_city', 'address_postcode', 'address_country'):
            if mutable.get(field) == '':
                mutable[field] = None
        if mutable.get('date_of_birth') == '':
            mutable['date_of_birth'] = None
        return super().to_internal_value(mutable)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
