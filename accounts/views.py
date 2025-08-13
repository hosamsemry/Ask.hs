from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from .forms import RegisterForm, LoginForm, UserProfileForm
from django.contrib.auth import logout
from django.contrib import messages
from .models import UserProfile, ProfileVisit
from questions.models import Answer
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.db import models
from user_notifications.views import send_follow_notification
from django.core.cache import cache

User = get_user_model()

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Registration successful! You can now log in.")
        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home') 

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=email.split("@")[0], password=password)

        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            form.add_error(None, 'Invalid email or password')
            return self.form_invalid(form)

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect(reverse('login'))

@method_decorator(login_required, name='dispatch')
class UserProfileView(DetailView):
    model = UserProfile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        if not hasattr(self, '_cached_profile'):
            cache_key = f"profile:{self.kwargs['username']}"
            profile = cache.get(cache_key)

            if profile is None:
                profile = get_object_or_404(
                    UserProfile.objects.filter(is_deleted=False, user__is_active=True).select_related('user'),
                    user__username=self.kwargs['username']
                )
                cache.set(cache_key, profile, timeout=120)

            self._cached_profile = profile
        return self._cached_profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        profile_user = profile.user

        if self.request.user.is_authenticated and self.request.user != profile_user:
            UserProfile.objects.filter(pk=profile.pk).update(
                visit_count=models.F('visit_count') + 1
            )

            ProfileVisit.objects.create(
                visitor=self.request.user,
                visited=profile_user,
                timestamp=timezone.now()
            )

        cache_key_questions = f"profile:{profile_user.id}:questions"
        questions = cache.get(cache_key_questions)
        if questions is None:
            questions_qs = (
                profile_user.questions_received
                .filter(is_deleted=False)
                .select_related('sender')
                .prefetch_related(
                    Prefetch(
                        'answer',
                        queryset=Answer.objects.select_related('responder', 'question')
                                                .prefetch_related('likes')
                    )
                )
            )
            questions = list(questions_qs)
            cache.set(cache_key_questions, questions, timeout=120)

        context['questions'] = questions

        if self.request.user == profile_user and profile.is_premium:
            cache_key_visitors = f"profile:{profile_user.id}:visitors"
            visitors = cache.get(cache_key_visitors)
            if visitors is None:
                visitors_qs = (
                    ProfileVisit.objects
                    .filter(visited=profile_user)
                    .select_related('visitor')
                    .order_by('-timestamp')
                )
                visitors = list(visitors_qs)
                cache.set(cache_key_visitors, visitors, timeout=120)
            context['visitors'] = visitors

        return context
    
class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/edit_profile.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self):
        return self.request.user.userprofile

    def form_valid(self, form):
        response = super().form_valid(form)
        cache_keys = [
            f'user_profile_{self.request.user.id}',
            f'user_profile_{self.request.user.username}',
            f'profile_data_{self.request.user.id}',
            f'user_answers_{self.request.user.id}',
            f'user_questions_{self.request.user.id}',
        ]
        cache.delete_many(cache_keys)
        
        cache.clear()  
        messages.success(self.request, "Profile updated successfully!")
        return response

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})

    

@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.userprofile
    current_profile = request.user.userprofile

    if target_profile != current_profile:
        if target_profile in current_profile.following.all():
            current_profile.following.remove(target_profile)
        else:
            current_profile.following.add(target_profile)
            send_follow_notification(followed_user=target_user, follower_user=request.user)

    next_url = request.META.get('HTTP_REFERER', reverse('profile', args=[username]))
    return redirect(next_url)

class FollowersListView(ListView):
    template_name = 'accounts/followers_list.html'
    context_object_name = 'profiles'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        page_number = self.request.GET.get('page', 1)
        cache_key = f"followers:{username}:page:{page_number}"

        queryset = cache.get(cache_key)
        if queryset is not None:
            return queryset

        user = get_object_or_404(User, username=username)
        queryset = user.userprofile.followers.filter(is_deleted=False)
        cache.set(cache_key, queryset, timeout=120)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewing_user'] = get_object_or_404(User, username=self.kwargs['username'])
        context['list_type'] = 'Followers'
        return context

class FollowingListView(ListView):
    template_name = 'accounts/following_list.html'
    context_object_name = 'profiles'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        page_number = self.request.GET.get('page', 1)
        cache_key = f"following:{username}:page:{page_number}"

        queryset = cache.get(cache_key)
        if queryset is not None:
            return queryset

        user = get_object_or_404(User, username=username)
        queryset = user.userprofile.following.filter(is_deleted=False)
        cache.set(cache_key, queryset, timeout=120)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewing_user'] = get_object_or_404(User, username=self.kwargs['username'])
        context['list_type'] = 'Following'
        return context

@login_required
def remove_follower(request, username):
    if request.method == 'POST':
        follower_user = get_object_or_404(User, username=username)
        follower_profile = follower_user.userprofile.filter(is_deleted=False)
        current_user_profile = request.user.userprofile

        if current_user_profile in follower_profile.following.all():
            follower_profile.following.remove(current_user_profile)

    return redirect('followers_list', request.user.username)

@method_decorator(login_required, name='dispatch')
class ProfileVisitorsView(ListView):
    model = ProfileVisit
    template_name = 'accounts/profile_visitors.html'
    context_object_name = 'visits'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.profile_user = get_object_or_404(
            User.objects.filter(is_active=True).select_related('userprofile'),
            username=self.kwargs['username']
        )

        if request.user != self.profile_user:
            raise PermissionDenied("You are not allowed to view this page.")

        if not self.profile_user.userprofile.is_premium:
            raise PermissionDenied("Upgrade to premium to view profile visitors.")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        username = self.kwargs['username']
        page_number = self.request.GET.get('page', 1)
        cache_key = f"profile_visitors:{username}:page:{page_number}"

        queryset = cache.get(cache_key)
        if queryset is not None:
            return queryset

        queryset = (
            ProfileVisit.objects
            .filter(visited=self.profile_user)
            .select_related('visitor', 'visitor__userprofile')
            .order_by('-timestamp')
        )
        cache.set(cache_key, queryset, timeout=120)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context 
@method_decorator(login_required, name='dispatch')
class SubscribeView(TemplateView):
    template_name = 'accounts/subscribe.html'

    def post(self, request, *args, **kwargs):
        profile = request.user.userprofile
        profile.is_premium = True
        profile.save()
        messages.success(request, "You’ve successfully upgraded to premium! It may take 2 minutes to take effect.")
        return redirect('profile', username=request.user.username)
    
@login_required
def deleted_account(request):
    if request.method == 'POST':
        profile = request.user.userprofile
        user = request.user
        user.is_active = False
        profile.is_deleted = True
        profile.save()
        logout(request)
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('register')
    return redirect('profile', username=request.user.username)
