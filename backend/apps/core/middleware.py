from django.conf import settings
from django.http import JsonResponse
from apps.organizations.models import Organization


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        slug = self._resolve_slug(request)
        if not slug:
            return JsonResponse({'error': 'Tenant not specified'}, status=400)
        try:
            request.tenant = Organization.objects.get(slug=slug, is_active=True)
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organisation not found'}, status=404)
        return self.get_response(request)

    def _resolve_slug(self, request):
        if settings.DEBUG:
            header_slug = request.headers.get('X-Tenant-Slug')
            if header_slug:
                return header_slug
        host = request.get_host().split(':')[0]
        parts = host.split('.')
        return parts[0] if len(parts) > 1 else None
