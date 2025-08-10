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
        return f"To {self.receiver.username} - {self.content[:30]}"


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    responder = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='AnswerLike', related_name='liked_answer')

    def __str__(self):
        return f"Answer to {self.question.receiver.username}"
    @property
    def likes_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()
    

from django.db import models
from django.conf import settings

class AnswerLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, related_name='liked')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')

    def __str__(self):
        return f'{self.user.username} liked answer {self.answer.id}'

