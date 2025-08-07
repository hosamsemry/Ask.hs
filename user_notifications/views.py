from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def send_like_notification(user, liker, answer):
    message = f"{liker.username} liked your answer."
    notification = Notification.objects.create(recipient=user, message=message,answer=answer,sender=liker,)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'send_notification',
            'message': message,
            'notification_id': notification.id,
        }
    )

def send_follow_notification(followed_user, follower_user):
    message = f"{follower_user.username} started following you."
    notification = Notification.objects.create(
        recipient=followed_user,
        sender=follower_user,
        message=message
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{followed_user.id}',
        {
            'type': 'send_notification',
            'message': message,
            'notification_id': notification.id,
        }
    )


@login_required
def fetch_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')
    data = []
    for n in notifications:
        if n.answer:
            url = f"/qa/answers/{n.answer.id}/"
        elif n.sender:
            url = f"/profile/{n.sender.username}/"
        else:
            url = "#"

        data.append({
            "id": n.id,
            "message": n.message,
            "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M"),
            "url": url
        })
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


@login_required
def mark_all_notifications_as_read(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    notifications.update(is_read=True)
    return JsonResponse({"success": True})


@login_required
def all_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')

    data = []
    for n in notifications:
        if n.answer:
            url = f"/qa/answers/{n.answer.id}/"
        elif n.sender:
            url = f"/profile/{n.sender.username}/"
        else:
            url = "#"

        data.append({
            "id": n.id,
            "message": n.message,
            "timestamp": n.timestamp,
            "is_read": n.is_read,
            "url": url,
        })

    return render(request, 'notifications/all_notifications.html', {'notifications': data})
