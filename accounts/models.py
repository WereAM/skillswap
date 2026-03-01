from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True
    )

    rating_average = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return f'{self.user.username} Profile'
