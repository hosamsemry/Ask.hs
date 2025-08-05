# qa/views.py

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from questions.models import Answer
from accounts.models import UserProfile

class Home(LoginRequiredMixin, ListView):
    model = Answer
    template_name = 'core/home.html'
    context_object_name = 'answers'

    def get_queryset(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        following_users = user_profile.following.all().values_list('user', flat=True)
        return Answer.objects.filter(responder__in=following_users).order_by('-created_at')

