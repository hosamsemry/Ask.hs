from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from questions.models import Answer
from accounts.models import UserProfile
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()
class Home(LoginRequiredMixin, ListView):
    model = Answer
    template_name = 'core/home.html'
    context_object_name = 'answers'
    paginate_by = 10

    def get_queryset(self):
        user_profile = (
            UserProfile.objects
            .prefetch_related('following__user')
            .get(user=self.request.user)
        )
        following_users_ids = user_profile.following.all().values_list('user__id', flat=True)

        return (
            Answer.objects
            .filter(responder__in=following_users_ids)
            .select_related(
                'responder__userprofile',
                'question',
                'question__sender',
            ).prefetch_related('likes')
            .order_by('-created_at')
        )


def search_users(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'users': []})

    starts_with = User.objects.filter(username__istartswith=query)
    contains = User.objects.filter(username__icontains=query).exclude(id__in=starts_with.values_list('id', flat=True))

    results = list(starts_with.values('username')) + list(contains.values('username'))
    return JsonResponse({'users': results})
