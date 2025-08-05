from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Question(models.Model):
    receiver = models.ForeignKey(User, related_name='questions_received', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='questions_sent', null=True, blank=True, on_delete=models.SET_NULL)
    is_anonymous = models.BooleanField(default=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.to_user.username} - {self.content[:30]}"


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    responder = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Answer to {self.question.to_user.username}"
    

from django.db import models
from django.conf import settings

class AnswerLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')

    def __str__(self):
        return f'{self.user.username} liked answer {self.answer.id}'

