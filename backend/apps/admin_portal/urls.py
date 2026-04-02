from django.urls import path
from apps.admin_portal import views

urlpatterns = [
    path('members/export/', views.MemberExportView.as_view(), name='admin-member-export'),
    path('members/<int:pk>/', views.MemberDetailView.as_view(), name='admin-member-detail'),
    path('members/', views.MemberListView.as_view(), name='admin-member-list'),
]
