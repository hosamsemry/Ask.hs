from .models import Question, Answer
from django import forms


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['content', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control mb-3',
                'rows': 3,
                'placeholder': 'Type your question here...',
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'content': 'Your Question',
            'is_anonymous': 'Ask anonymously',
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control mb-3',
                'rows': 4,
                'placeholder': 'Write your answer here...',
            }),
        }
        labels = {
            'content': 'Your Answer',
        }
