from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from .forms import RegisterForm, LoginForm
from django.contrib.auth import logout
from django.contrib import messages
from .models import UserProfile


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
        return get_object_or_404(UserProfile, user__username=self.kwargs['username'])