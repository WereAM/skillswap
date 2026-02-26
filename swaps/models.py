from django.db import models
from django.contrib.auth.models import User
from skills.models import UserSkill

class SwapRequests(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
    ]

    sender = models.ForeignKey(
        User, on_dlete=models.CASCADE,
        related_name='sent_requests'
    )
    
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='received_requests'
    )

    offered_skill = models.ForeignKey(
        UserSkill, on_delete=models.CASCADE,
        related_name='offered_in_swaps'
    )

    requested_skill = models.ForeignKey(
        UserSkill, on_delete=models.CASCADE,
        related_name='requested_in_swaps'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sender} -> {self.receiver} ({self.status})'
    
class Session(models.Model):
    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (SCHEDULED, 'Scheduled'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    swap_request = models.OneToOneField(
        SwapRequests, on_delete=models.CASCADE,
        related_name='session'
    )

    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    meeting_link = models.URLField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=SCHEDULED
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'Session for {self.swap_request} on {self.scheduled_date}'
    
class Review(models.Model):
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE,
        related_name='reviews'
    )

    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews_given'
    )

    reviewee = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews_received'
    )

    rating = models.PositiveSmallIntegerField() # 1 - 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # restrict one review per reviewer per session
    class Meta:
        unique_together = {'session', 'reviewer'}

    def __str__(self):
        return f'{self.reviewer} reviewed {self.reviewee} ({self.rating}/5)'