from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.eligibility import is_event_eligible
from apps.events.models import Event, EventCategory
from apps.events.pagination import EventPagination
from apps.events.serializers import EventCategorySerializer, EventSerializer


class EventListView(APIView):
    """Public list of published and cancelled events. No auth required."""

    def get(self, request):
        qs = Event.objects.for_tenant(request.tenant).filter(
            status__in=['published', 'cancelled']
        ).order_by('start_datetime')

        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        date_from = request.query_params.get('date_from')
        if date_from:
            qs = qs.filter(start_datetime__date__gte=date_from)

        date_to = request.query_params.get('date_to')
        if date_to:
            qs = qs.filter(start_datetime__date__lte=date_to)

        paginator = EventPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = EventSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class EventCategoryListView(APIView):
    """Public list of event categories. No auth required."""

    def get(self, request):
        categories = EventCategory.objects.for_tenant(request.tenant).order_by('name')
        serializer = EventCategorySerializer(categories, many=True)
        return Response(serializer.data)


class EventDetailView(APIView):
    """Public event detail. 404 for draft/archived or wrong org."""

    def get(self, request, pk):
        try:
            event = Event.objects.for_tenant(request.tenant).get(
                pk=pk, status__in=['published', 'cancelled']
            )
        except ObjectDoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data)


class EventAgendaView(APIView):
    """Authenticated member agenda: up to 5 upcoming eligible published events."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        qs = Event.objects.for_tenant(request.tenant).filter(
            status='published',
            start_datetime__gt=now,
        ).order_by('start_datetime').prefetch_related('restricted_to_tiers')

        eligible = []
        for event in qs:
            if is_event_eligible(event, request.user):
                eligible.append(event)
            if len(eligible) >= 5:
                break

        serializer = EventSerializer(eligible, many=True, context={'request': request})
        return Response({'count': len(eligible), 'results': serializer.data})
