from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', include('apps.organizations.urls')),
    path('api/v1/config/', include('apps.organizations.config_urls')),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/contact/', include('apps.contact.urls')),
]
