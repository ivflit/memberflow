from django.urls import path
from apps.events.admin_views import (
    AdminEventCategoryListView,
    AdminEventCategoryDetailView,
    AdminEventListView,
    AdminEventDetailView,
)

urlpatterns = [
    path('categories/', AdminEventCategoryListView.as_view(), name='admin-event-category-list'),
    path('categories/<int:pk>/', AdminEventCategoryDetailView.as_view(), name='admin-event-category-detail'),
    path('<int:pk>/', AdminEventDetailView.as_view(), name='admin-event-detail'),
    path('', AdminEventListView.as_view(), name='admin-event-list'),
]
