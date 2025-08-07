from django.db import models
from django.contrib.auth import get_user_model
from questions.models import Answer

User = get_user_model()
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)


    def __str__(self):
        return f'Notification for {self.recipient.username}'
