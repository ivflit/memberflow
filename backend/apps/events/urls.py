from django.urls import path
from apps.events.views import (
    EventCategoryListView,
    EventAgendaView,
    EventDetailView,
    EventListView,
)

urlpatterns = [
    path('categories/', EventCategoryListView.as_view(), name='event-category-list'),
    path('agenda/', EventAgendaView.as_view(), name='event-agenda'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('', EventListView.as_view(), name='event-list'),
]
