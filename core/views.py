from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from questions.models import Answer
from accounts.models import UserProfile
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.encoding import force_str
from django.contrib.auth import logout
from django.contrib import messages

User = get_user_model()
from django.core.cache import cache
from django.utils.encoding import force_str

class Home(LoginRequiredMixin, ListView):
    model = Answer
    template_name = 'core/home.html'
    context_object_name = 'answers'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        try:
            user_profile = UserProfile.objects.filter(is_deleted=False).prefetch_related('following__user').get(user=user)
        except UserProfile.DoesNotExist:
            logout(self.request)
            messages.error(self.request, "Your account has been deleted or deactivated.")
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("User profile does not exist or is deleted.")

        user_id = user.id
        page_number = force_str(self.request.GET.get('page', 1))
        cache_key = f"user_feed:{user_id}:page:{page_number}"

        queryset = cache.get(cache_key)
        if queryset is not None:
            return queryset

        following_users_ids = user_profile.following.all().values_list('user__id', flat=True)

        queryset = (
            Answer.objects
            .filter(responder__in=following_users_ids)
            .select_related(
                'responder__userprofile',
                'question',
                'question__sender',
            ).prefetch_related('likes')
            .order_by('-created_at')
        )

        cache.set(cache_key, queryset, timeout=120)
        return queryset


def search_users(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'users': []})

    starts_with = User.objects.filter(
        is_active=True,
        userprofile__is_deleted=False,
        username__istartswith=query
    )
    contains = User.objects.filter(
        is_active=True,
        userprofile__is_deleted=False,
        username__icontains=query
    ).exclude(id__in=starts_with.values_list('id', flat=True))

    results = list(starts_with.values('username')) + list(contains.values('username'))
    return JsonResponse({'users': results})
