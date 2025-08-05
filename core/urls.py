from django.urls import path
from .views import Home, search_users

urlpatterns = [
    path('home/', Home.as_view(), name='home'),
    path('search-users/', search_users, name='search_users'),
]
