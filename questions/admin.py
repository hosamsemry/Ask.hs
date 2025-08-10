from django.contrib import admin
from .models import Question, Answer, AnswerLike
# Register your models here.


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display= [
        'sender', 'receiver', 'created_at', 'is_answered'
    ]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    pass

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    pass