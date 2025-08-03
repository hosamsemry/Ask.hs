from django.urls import path
from .views import RegisterView, LoginView, logout_view, UserProfileView, EditProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('u/<str:username>/', UserProfileView.as_view(), name='profile'),
     path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
]
