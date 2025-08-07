from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


def send_like_notification(user, liker):
    message = f"{liker.username} liked your answer."
    notification = Notification.objects.create(recipient=user, message=message)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'send_notification',
            'message': message,
            'notification_id': notification.id,
        }
    )

