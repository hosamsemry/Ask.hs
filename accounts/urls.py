from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('u/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
    path('follow/<str:username>/', toggle_follow, name='toggle_follow'),
    path('<str:username>/followers/', FollowersListView.as_view(), name='followers_list'),
    path('<str:username>/following/', FollowingListView.as_view(), name='following_list'),
    path('remove-follower/<str:username>/', remove_follower, name='remove_follower'),
    path('<str:username>/visitors/', ProfileVisitorsView.as_view(), name='profile-visitors'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('delete/', deleted_account, name='delete_account'),

]
