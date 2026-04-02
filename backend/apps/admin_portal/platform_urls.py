from django.urls import path
from apps.admin_portal import views

urlpatterns = [
    path('members/<int:pk>/', views.PlatformMemberDetailView.as_view(), name='platform-member-detail'),
]
