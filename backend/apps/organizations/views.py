from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    if request.tenant is None:
        return Response({'error': 'Tenant not specified'}, status=400)
    return Response({
        'status': 'ok',
        'tenant': request.tenant.slug,
    })


@api_view(['GET'])
def config(request):
    """Public endpoint — returns current tenant's config for frontend bootstrap.
    Returns 404 if no tenant is in scope (root/platform domain).
    """
    if request.tenant is None:
        return Response({'error': 'No tenant in scope'}, status=404)
    try:
        cfg = request.tenant.config
        branding = cfg.branding or {}
        allow_self_registration = cfg.allow_self_registration
    except Exception:
        branding = {}
        allow_self_registration = False

    return Response({
        'name': request.tenant.name,
        'slug': request.tenant.slug,
        'branding': branding,
        'features': {
            'allow_self_registration': allow_self_registration,
        },
    })
