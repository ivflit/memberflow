from rest_framework import serializers
from apps.events.models import EventCategory, Event
from apps.events.eligibility import is_event_eligible
from apps.memberships.models import MembershipTier


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ['id', 'name', 'colour']


class EventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True, allow_null=True)
    is_restricted = serializers.SerializerMethodField()
    is_eligible = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_datetime', 'end_datetime',
            'venue_name', 'venue_postcode', 'category', 'image_url', 'status',
            'is_restricted', 'is_eligible',
        ]

    def get_is_restricted(self, obj):
        return obj.restricted_to_tiers.exists() or bool(obj.restricted_to_roles)

    def get_is_eligible(self, obj):
        request = self.context.get('request')
        user = None
        if request is not None and request.user is not None:
            try:
                if request.user.is_authenticated:
                    user = request.user
            except AttributeError:
                user = None
        return is_event_eligible(obj, user)


# ── Admin serializers ──────────────────────────────────────────────────────────

class AdminEventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ['id', 'name', 'colour']

    def validate_name(self, value):
        request = self.context.get('request')
        if request is None:
            return value
        qs = EventCategory.objects.for_tenant(request.tenant).filter(name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A category with this name already exists.')
        return value


class AdminEventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    restricted_to_tiers = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=MembershipTier.objects.none(),  # overridden in __init__ to be tenant-scoped
    )
    restricted_to_roles = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=False,
        default=list,
    )

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_datetime', 'end_datetime',
            'venue_name', 'venue_postcode', 'category', 'category_id', 'image_url',
            'status', 'restricted_to_tiers', 'restricted_to_roles',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        from apps.memberships.models import MembershipTier
        if request is not None:
            self.fields['restricted_to_tiers'].child_relation.queryset = (
                MembershipTier.objects.for_tenant(request.tenant)
            )
        else:
            self.fields['restricted_to_tiers'].child_relation.queryset = (
                MembershipTier.objects.none()
            )

    def validate_restricted_to_tiers(self, value):
        """Ensure all tiers belong to the current tenant."""
        request = self.context.get('request')
        if not request or not value:
            return value
        from apps.memberships.models import MembershipTier
        valid_ids = set(
            MembershipTier.objects.for_tenant(request.tenant).values_list('id', flat=True)
        )
        for tier in value:
            if tier.id not in valid_ids:
                raise serializers.ValidationError(
                    'One or more tiers do not belong to this organisation'
                )
        return value

    def validate(self, attrs):
        start = attrs.get('start_datetime') or (
            self.instance.start_datetime if self.instance else None
        )
        end = attrs.get('end_datetime') or (
            self.instance.end_datetime if self.instance else None
        )
        if start and end and end <= start:
            raise serializers.ValidationError(
                {'end_datetime': 'end_datetime must be after start_datetime'}
            )

        request = self.context.get('request')
        if request is not None:
            category_id = attrs.get('category_id')
            if category_id is not None:
                try:
                    EventCategory.objects.for_tenant(request.tenant).get(pk=category_id)
                except EventCategory.DoesNotExist:
                    raise serializers.ValidationError(
                        {'category_id': 'Category does not belong to this organisation'}
                    )

        return attrs

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        tiers = validated_data.pop('restricted_to_tiers', [])
        event = Event(**validated_data)
        if category_id is not None:
            event.category_id = category_id
        event.save()
        event.restricted_to_tiers.set(tiers)
        return event

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', ...)
        tiers = validated_data.pop('restricted_to_tiers', ...)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if category_id is not ...:
            instance.category_id = category_id

        instance.save()

        if tiers is not ...:
            instance.restricted_to_tiers.set(tiers)

        return instance
