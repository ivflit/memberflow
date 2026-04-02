from rest_framework.permissions import BasePermission
from apps.users.models import UserOrganizationRole


class IsOrgAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'organization_id'):
            return False
        try:
            role = UserOrganizationRole.objects.get(
                user=request.user, organization_id=request.user.organization_id
            )
            return role.role in ('org_admin',)
        except UserOrganizationRole.DoesNotExist:
            return False


class IsOrgStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'organization_id'):
            return False
        try:
            role = UserOrganizationRole.objects.get(
                user=request.user, organization_id=request.user.organization_id
            )
            return role.role in ('org_admin', 'org_staff')
        except UserOrganizationRole.DoesNotExist:
            return False


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'organization_id'):
            return False
        try:
            role = UserOrganizationRole.objects.get(
                user=request.user, organization_id=request.user.organization_id
            )
            return role.role == 'platform_admin'
        except UserOrganizationRole.DoesNotExist:
            return False
