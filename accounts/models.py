from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta

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
    
class EmailVerificationToken(models.Model):
    '''
    Stores a unique token for each email verification request
    Token should expire after 1 hour
    '''

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='verification_token'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=1)
    
    def __str__(self):
        return f'Verification token for {self.user.username}'