from messaging.models import Notification

def create_notification(user, notification_type, content):
    '''
    Called from a view whenever an event happens and creates a notification
    User is the receiver
    '''

    Notification.objects.create(
        user = user,
        notification_type = notification_type,
        content = content,
        is_read = False
    )