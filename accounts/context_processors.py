"""
makes unread message and notification count available on every page/template automatically
 without adding it to every view
"""

from messaging.models import Message, Notification

def unread_messages(request):
    if request.user.is_authenticated:
        unread_msg_count = Message.objects.filter(
            receiver = request.user,
            is_read = False
        ).count()

        unread_notification_count = Notification.objects.filter(
            user = request.user,
            is_read = False
        ).count()

        return {
            'unread_messages_count': unread_msg_count,
            'unread_notifications_count': unread_notification_count,
            }
    
    return {
        'unread_messages_count': 0,
        'unread_notifications_count': 0,
        }
