from django.db import models
from django.contrib.auth.models import AbstractUser



# Create your models here.
class UserAccount(AbstractUser):

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='userprofile')
    bio = models.TextField(blank=True)
    picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.user.email
