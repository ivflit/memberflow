from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOrgAdmin, IsOrgStaff
from apps.events.models import Event, EventCategory
from apps.events.pagination import EventPagination
from apps.events.serializers import (
    AdminEventCategorySerializer,
    AdminEventSerializer,
    EventSerializer,
)


class AdminEventCategoryListView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOrgStaff()]
        return [IsOrgAdmin()]

    def get(self, request):
        categories = EventCategory.objects.for_tenant(request.tenant).order_by('name')
        serializer = AdminEventCategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminEventCategorySerializer(
            data=request.data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        category = serializer.save(organization=request.tenant)
        return Response(
            AdminEventCategorySerializer(category).data,
            status=status.HTTP_201_CREATED,
        )


class AdminEventCategoryDetailView(APIView):

    def get_permissions(self):
        return [IsOrgAdmin()]

    def _get_category(self, request, pk):
        try:
            return EventCategory.objects.for_tenant(request.tenant).get(pk=pk)
        except ObjectDoesNotExist:
            return None

    def patch(self, request, pk):
        category = self._get_category(request, pk)
        if category is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminEventCategorySerializer(
            category, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        category = serializer.save()
        return Response(AdminEventCategorySerializer(category).data)

    def delete(self, request, pk):
        category = self._get_category(request, pk)
        if category is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if category.events.exists():
            return Response(
                {'detail': 'Cannot delete a category that has events attached.'},
                status=status.HTTP_409_CONFLICT,
            )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminEventListView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOrgStaff()]
        return [IsOrgAdmin()]

    def get(self, request):
        qs = Event.objects.for_tenant(request.tenant).order_by('start_datetime')

        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        paginator = EventPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = AdminEventSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AdminEventSerializer(
            data=request.data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        event = serializer.save(organization=request.tenant)
        return Response(
            AdminEventSerializer(event, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminEventDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOrgStaff()]
        return [IsOrgAdmin()]

    def _get_event(self, request, pk):
        try:
            return Event.objects.for_tenant(request.tenant).get(pk=pk)
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        event = self._get_event(request, pk)
        if event is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminEventSerializer(event, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        event = self._get_event(request, pk)
        if event is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminEventSerializer(
            event, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        event = serializer.save()
        return Response(AdminEventSerializer(event, context={'request': request}).data)

    def delete(self, request, pk):
        event = self._get_event(request, pk)
        if event is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if event.status != 'draft':
            return Response(
                {'detail': 'Only draft events can be deleted. Use "archived" status to remove from public view.'},
                status=status.HTTP_409_CONFLICT,
            )
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
