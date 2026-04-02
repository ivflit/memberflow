import csv

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOrgAdmin, IsOrgStaff, IsPlatformAdmin
from apps.users.models import User, UserOrganizationRole
from apps.admin_portal.serializers import MemberListSerializer, MemberDetailSerializer


class MemberListView(APIView):
    permission_classes = [IsOrgStaff]

    def get(self, request):
        members = User.objects.for_tenant(request.tenant).order_by('last_name', 'first_name')
        serializer = MemberListSerializer(members, many=True)
        return Response(serializer.data)


class MemberDetailView(APIView):
    permission_classes = [IsOrgStaff]

    def get(self, request, pk):
        try:
            member = User.objects.for_tenant(request.tenant).get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MemberDetailSerializer(member).data)


class MemberExportView(APIView):
    permission_classes = [IsOrgAdmin]

    def get_queryset(self, request):
        return User.objects.for_tenant(request.tenant).order_by('last_name', 'first_name')

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="members.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'id', 'email', 'first_name', 'last_name', 'date_of_birth',
            'address_street', 'address_city', 'address_postcode', 'address_country',
            'role', 'is_active', 'created_at',
        ])

        role_map = {
            r.user_id: r.role
            for r in UserOrganizationRole.objects.filter(organization=request.tenant)
        }

        for member in self.get_queryset(request):
            writer.writerow([
                member.id,
                member.email,
                member.first_name,
                member.last_name,
                member.date_of_birth.isoformat() if member.date_of_birth else '',
                member.address_street or '',
                member.address_city or '',
                member.address_postcode or '',
                member.address_country or '',
                role_map.get(member.id, 'member'),
                member.is_active,
                member.created_at.isoformat(),
            ])

        return response


class PlatformMemberDetailView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request, pk):
        try:
            member = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MemberDetailSerializer(member).data)

    def patch(self, request, pk):
        try:
            member = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        from apps.users.serializers import ProfileUpdateSerializer
        serializer = ProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        for field in ('date_of_birth', 'address_street', 'address_city',
                      'address_postcode', 'address_country'):
            if field in data:
                setattr(member, field, data[field])
        member.save()
        return Response(MemberDetailSerializer(member).data)
