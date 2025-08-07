from django.urls import path
from .views import *

urlpatterns = [
    path('ask/<str:username>/', AskQuestionView.as_view(), name='ask_question'),
    path('answer/<int:question_id>/', AnswerQuestionView.as_view(), name='answer_question'),
    path('unanswered/', UnansweredQuestionListView.as_view(), name='unanswered_questions'),
    path('question/<int:question_id>/delete/', delete_question, name='delete_question'),
    path('like/<int:answer_id>/', toggle_like, name='toggle_like'),
    path("answers/<int:pk>/", answer_detail, name="answer_detail"),
]
