from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Question, Answer, AnswerLike
from .forms import QuestionForm, AnswerForm
from django.http import JsonResponse
from user_notifications.views import send_like_notification
User = get_user_model()


class AskQuestionView(LoginRequiredMixin, FormView):
    template_name = 'qa/ask_question.html'
    form_class = QuestionForm

    def dispatch(self, request, *args, **kwargs):
        self.receiver = get_object_or_404(User, username=kwargs['username'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        question = form.save(commit=False)
        question.receiver = self.receiver
        if not form.cleaned_data['is_anonymous']:
            question.sender = self.request.user
        question.save()
        return redirect('profile', username=self.receiver.username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['receiver'] = self.receiver
        return context


class AnswerQuestionView(LoginRequiredMixin, View):
    template_name = 'qa/answer_question.html'
    form_class = AnswerForm

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, id=kwargs['question_id'], receiver=request.user)

        if hasattr(self.question, 'answer'):
            return redirect('profile', username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'question': self.question})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.responder = request.user
            answer.question = self.question
            answer.save()
            self.question.is_answered = True
            self.question.save()
            return redirect('profile', username=request.user.username)
        return render(request, self.template_name, {'form': form, 'question': self.question})



class UnansweredQuestionListView(LoginRequiredMixin, ListView):
    model = Question
    template_name = 'qa/unanswered_questions.html'
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.filter(
            receiver=self.request.user,
            answer__isnull=True,is_deleted=False
        ).order_by('-created_at')
    

@login_required
@require_POST
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, receiver=request.user)
    question.is_deleted = True
    question.save()
    return redirect('profile', request.user.username)

@login_required
def toggle_like(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    if request.method == 'POST':
        if request.user in answer.likes.all():
            answer.likes.remove(request.user)
        else:
            answer.likes.add(request.user)
            send_like_notification(user=answer.responder, liker=request.user)
        return JsonResponse({'likes_count': answer.likes.count()})
    return JsonResponse({'error': 'Invalid method'}, status=400)