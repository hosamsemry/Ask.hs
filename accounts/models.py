from django.db import models
from django.contrib.auth.models import AbstractUser



# Create your models here.
class UserAccount(AbstractUser):
    first_name = None
    last_name = None
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='userprofile')
    bio = models.TextField(blank=True)
    picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    visit_count = models.PositiveIntegerField(default=0)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
