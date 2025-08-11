from django.urls import path
from .views import Home, search_users

urlpatterns = [
    
    path('search-users/', search_users, name='search_users'),
]
