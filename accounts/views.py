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
from django.db.models import Prefetch
from django.db import models
User = get_user_model()

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
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


class UserProfileView(DetailView):
    model = UserProfile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        if not hasattr(self, '_cached_profile'):
            self._cached_profile = get_object_or_404(
                UserProfile.objects.select_related('user'),
                user__username=self.kwargs['username']
            )
        return self._cached_profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        profile_user = profile.user

        if self.request.user.is_authenticated and self.request.user != profile_user:
            UserProfile.objects.filter(pk=profile.pk).update(visit_count=models.F('visit_count') + 1)

            ProfileVisit.objects.create(
                visitor=self.request.user,
                visited=profile_user,
                timestamp=timezone.now()
            )

        questions = (
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

        context['questions'] = questions

        if self.request.user == profile_user and profile.is_premium:
            context['visitors'] = (
                ProfileVisit.objects
                .filter(visited=profile_user)
                .select_related('visitor')  # avoids query per visitor
                .order_by('-timestamp')
            )

        return context

    
class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/edit_profile.html'

    def get_object(self):
        return self.request.user.userprofile

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

    next_url = request.META.get('HTTP_REFERER', reverse('profile', args=[username]))
    return redirect(next_url)

class FollowersListView(ListView):
    template_name = 'accounts/followers_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.userprofile.followers.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewing_user'] = get_object_or_404(User, username=self.kwargs['username'])
        context['list_type'] = 'Followers'
        return context


class FollowingListView(ListView):
    template_name = 'accounts/following_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.userprofile.following.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewing_user'] = get_object_or_404(User, username=self.kwargs['username'])
        context['list_type'] = 'Following'
        return context


@login_required
def remove_follower(request, username):
    if request.method == 'POST':
        follower_user = get_object_or_404(User, username=username)
        follower_profile = follower_user.userprofile
        current_user_profile = request.user.userprofile

        if current_user_profile in follower_profile.following.all():
            follower_profile.following.remove(current_user_profile)

    return redirect('followers_list', request.user.username)

@method_decorator(login_required, name='dispatch')
class ProfileVisitorsView(ListView):
    model = ProfileVisit
    template_name = 'accounts/profile_visitors.html'
    context_object_name = 'visits'

    def get_queryset(self):
        profile_user = get_object_or_404(UserProfile, user__username=self.kwargs['username']).user

        if self.request.user != profile_user:
            return ProfileVisit.objects.none()

        if not self.request.user.userprofile.is_premium:
            return ProfileVisit.objects.none()

        return ProfileVisit.objects.filter(visited=profile_user).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = get_object_or_404(UserProfile, user__username=self.kwargs['username']).user
        return context
    
@method_decorator(login_required, name='dispatch')
class SubscribeView(TemplateView):
    template_name = 'accounts/subscribe.html'

    def post(self, request, *args, **kwargs):
        profile = request.user.userprofile
        profile.is_premium = True
        profile.save()
        messages.success(request, "You’ve successfully upgraded to premium!")
        return redirect('profile', username=request.user.username)