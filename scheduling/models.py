from django.db import models
from django.contrib.auth.models import User
import pytz
import secrets

TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]

DAYS_OF_WEEK = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]

class SchedulingPreference(models.Model):
    '''Model to manage a user's schedule preferences.
    Only 1 per user, created automatically on first visit to scheduling page.
    '''          
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='scheduling_preference')   
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    # minimum gap between sessions in minutes
    buffer_minutes = models.PositiveIntegerField(default=15)
    # session_reminders
    reminder_hours = models.PositiveIntegerField(default=24)
    # Google calendar token stored as JSON string
    google_calendar_token = models.TextField(blank=True)
    google_calendar_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.user.username} Scheduling Preferences (Timezone: {self.timezone})'

class AvailabilitySlots(models.Model):
    '''A recurring weekly avaiability window for a user, e.g. 'Every Monday 6pm-8pm.
    Used by the smart suggestion engine to find mutual free timeslots.
    '''    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        day = dict(DAYS_OF_WEEK)[self.day_of_week]
        return f'{self.user.username}: {day} {self.start_time} - {self.end_time}'
    
class APIClient(models.Model):
    """
    Each external client/app/developer gets a unique API key for authentication.
    """

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='api_clients'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    api_key = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # track usage
    request_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # auto generate API key on creation
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.owner.username})'