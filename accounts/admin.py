from django.contrib import admin
from .models import UserAccount, UserProfile
# Register your models here.


@admin.register(UserAccount)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['username','first_name', 'last_name']


@admin.register(UserProfile)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['bio', 'location', 'birth_date']