from django.urls import path
from .views import mark_notification_as_read, fetch_notifications, mark_all_notifications_as_read

urlpatterns = [
    path('fetch/', fetch_notifications, name='fetch_notifications'),
    path('mark-as-read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
    path('mark-all-read/', mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
]
