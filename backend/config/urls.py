from django.contrib import admin
from django.urls import path, include
from apps.users.urls import profile_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', include('apps.organizations.urls')),
    path('api/v1/config/', include('apps.organizations.config_urls')),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/profile/', include(profile_urlpatterns)),
    path('api/v1/contact/', include('apps.contact.urls')),
    path('api/v1/admin/', include('apps.admin_portal.urls')),
    path('api/v1/platform/', include('apps.admin_portal.platform_urls')),
]
