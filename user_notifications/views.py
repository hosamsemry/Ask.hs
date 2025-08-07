from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


def send_like_notification(user, liker, answer):
    message = f"{liker.username} liked your answer."
    notification = Notification.objects.create(recipient=user, message=message,answer=answer,)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'send_notification',
            'message': message,
            'notification_id': notification.id,
        }
    )


@login_required
def fetch_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')
    data = [
        {
            "id": n.id,
            "message": n.message,
            "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M"),
            "answer_id": n.answer.id if n.answer else None,
            "url": f"/qa/answers/{n.answer.id}/" if n.answer else "#"
        }
        for n in notifications
    ]
    return JsonResponse({"notifications": data})



@login_required
def mark_notification_as_read(request, notification_id):
    if request.method == "POST":
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({"success": True})
        except Notification.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"}, status=404)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
