from datetime import date
from rest_framework import serializers
from apps.users.models import User, UserOrganizationRole


def _calculate_age(date_of_birth):
    if date_of_birth is None:
        return None
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


class MemberListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'age', 'created_at']

    def get_role(self, obj):
        try:
            return UserOrganizationRole.objects.get(
                user=obj, organization_id=obj.organization_id
            ).role
        except UserOrganizationRole.DoesNotExist:
            return 'member'

    def get_age(self, obj):
        return _calculate_age(obj.date_of_birth)


class MemberDetailSerializer(MemberListSerializer):
    class Meta(MemberListSerializer.Meta):
        fields = MemberListSerializer.Meta.fields + [
            'date_of_birth', 'address_street', 'address_city',
            'address_postcode', 'address_country',
        ]
