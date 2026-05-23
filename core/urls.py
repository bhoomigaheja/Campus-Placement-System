from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/read/<int:pk>/', views.mark_as_read, name='notification_read'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='notification_mark_all_read'),
]
