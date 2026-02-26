from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='received_messages'
    )

    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} -> {self.receiver} at {self.sent_at}'
    
class Notification(models.Model):
    SWAP_REQUEST = 'swap_request'
    SWAP_ACCEPTED = 'swap_accepted'
    SWAP_REJECTED = 'swap_rejected'
    SESSION_SCHEDULED = 'session_scheduled'
    NEW_MESSAGE = 'new_message'
    NEW_REVIEW = 'new_review'

    TYPE_CHOICES = [
        (SWAP_REQUEST, 'Swap Request'),
        (SWAP_ACCEPTED, 'Swap Accepted'),
        (SWAP_REJECTED, 'Swap Rejected'),
        (SESSION_SCHEDULED, 'Session Scheduled'),
        (NEW_MESSAGE, 'New Message'),
        (NEW_REVIEW, 'New Review'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notificatio for {self.user} - {self.notification_type}'