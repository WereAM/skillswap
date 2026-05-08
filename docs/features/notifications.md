# Notifications

## Overview

The notification system keeps users informed about important platform events without them needing to actively check every section of the app. Notifications are created automatically when significant events occur - swap requests, acceptances, new messages, reviews - and displayed in a dedicated notifications page with an unread badge in the navbar.

## How it Works

### Notification Creation

Notifications are created by calling a utility function from whichever view triggers the event:

```
Event occurs (e.g. swap accepted)
    → view calls create_notification(user, type, content)
        → Notification object created in database
            → Unread count incremented automatically
                → Badge appears in navbar on next page load
```

### Reading Notifications

```
User sees badge in navbar
    → clicks Notifications
        → all notifications listed, unread highlighted
            → user clicks "Mark read" on individual
                OR clicks "Mark all as read"
                    → is_read=True, badge count decreases
```

## Technical Implementation

### Model (`messaging/models.py`)

**`Notification`**

```python
class Notification(models.Model):
    TYPE_CHOICES = [
        ('swap_request', 'Swap Request'),
        ('swap_accepted', 'Swap Accepted'),
        ('swap_rejected', 'Swap Rejected'),
        ('session_scheduled', 'Session Scheduled'),
        ('new_message', 'New Message'),
        ('new_review', 'New Review'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Utility Function (`messaging/utils.py`)

The utility function is the single point of notification creation used by all other apps:

```python
from .models import Notification

def create_notification(user, notification_type, content):
    """
    Creates a notification for a user.
    Called from views whenever a significant event happens.

    Args:
        user: User object who receives the notification
        notification_type: string matching one of TYPE_CHOICES
        content: human-readable notification message
    """
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        content=content,
        is_read=False
    )
```

### Where Notifications Are Created

| Event | File | Recipient | Type |
|---|---|---|---|
| Swap request sent | `swaps/views.py` → `create_swap` | Receiver | `swap_request` |
| Swap accepted | `swaps/views.py` → `accept_swap` | Sender | `swap_accepted` |
| Swap denied | `swaps/views.py` → `deny_swap` | Sender | `swap_rejected` |
| Swap cancelled | `swaps/views.py` → `cancel_swap` | Receiver | `swap_rejected` |
| Session completed | `swaps/views.py` → `complete_session` | Other participant | `session_scheduled` |
| New message | `messaging/views.py` → `conversation` | Receiver | `new_message` |
| Review left | `swaps/views.py` → `leave_review` | Reviewee | `new_review` |

### Usage Pattern in Views

```python
from messaging.utils import create_notification

# In swaps/views.py after accepting a swap:
create_notification(
    user=swap.sender,
    notification_type='swap_accepted',
    content=f'{request.user.username} accepted your swap request - '
            f'{swap.offered_skill.skill.name} ⇄ {swap.requested_skill.skill.name}'
)
```

### Views (`messaging/views.py`)

| View | Purpose |
|---|---|
| `notifications` | Lists all notifications for current user |
| `mark_read` | Marks single notification as read |
| `mark_all_read` | Marks all notifications as read via bulk update |

**`mark_all_read`** uses `.update()` for efficiency:

```python
def mark_all_read(request):
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)  # Single SQL UPDATE, not N individual saves
    return redirect('messaging:notifications')
```

### Context Processor (`accounts/context_processors.py`)

Both unread counts are provided to every template via the context processor:

```python
def unread_messages(request):
    if request.user.is_authenticated:
        return {
            'unread_messages_count': Message.objects.filter(
                receiver=request.user, is_read=False
            ).count(),
            'unread_notifications_count': Notification.objects.filter(
                user=request.user, is_read=False
            ).count(),
        }
    return {'unread_messages_count': 0, 'unread_notifications_count': 0}
```

This runs on every request. Two database queries per request is acceptable at current scale. This can be optimised with caching later.

## URLs

| URL | Name | Auth Needed | Description |
|---|---|---|---|
| `/messaging/notifications/` | `messaging:notifications` | Yes | All notifications |
| `/messaging/notifications/<pk>/read/` | `messaging:mark_read` | Yes | Mark one as read |
| `/messaging/notifications/read-all/` | `messaging:mark_all_read` | Yes | Mark all as read |

## UI Design

### Notification Icons

Each notification type has a distinct icon for quick scanning:

| Type | Icon |
|---|---|
| `swap_request` | 🔄 |
| `swap_accepted` | ✅ |
| `swap_rejected` | ❌ |
| `new_message` | 💬 |
| `new_review` | ⭐ |
| `session_scheduled` | 📅 |
| Other | 🔔 |

### Unread State

Unread notifications have:
- Bold content text (`fw-bold` class)
- Teal left border on the card
- "Mark read" button visible

Read notifications have:
- Normal weight text
- No border highlight
- No action button

### Navbar Badge

The notification count appears on the username dropdown:

```html
{{ user.username }}
{% if unread_notifications_count > 0 %}
    <span class="badge bg-warning text-dark ms-1">
        {{ unread_notifications_count }}
    </span>
{% endif %}
```

## Key Design Decisions

### Why a utility function rather than Django signals?
Django signals (`post_save`, etc.) would decouple notification creation from the views, but add complexity that's harder to understand and debug for a small team. The utility function pattern is explicit - you can see exactly where every notification is created by searching for `create_notification` in the codebase. This tradeoff favours clarity over decoupling at current scale.

### Why store notifications in the database rather than a cache?
Database-backed notifications persist across sessions and server restarts. Users can see their notification history and mark things as read. A cache-only approach would lose notifications on server restart and couldn't support the read/unread state management.

### Why bulk `.update()` for mark all read?
Iterating through notifications and calling `.save()` on each triggers a separate SQL UPDATE per notification. `.update()` performs a single SQL UPDATE for all matching records regardless of count. This is fast for users with many notifications.

### Why put the Notification model in the messaging app?
Notifications and messages are both communication-layer concerns as they inform users about things happening on the platform. Grouping them in `messaging` keeps related functionality together and avoids creating a fourth app for a relatively small feature.

## Known Limitations

- No real-time delivery - notifications only appear on next page load
- No email notifications for platform events (only email verification implemented)
- No notification preferences - users can't choose which events to be notified about
- Context processor runs two DB queries on every request - not cached
- No notification grouping (10 messages from same user shows as 10 separate notifications)

## Future Improvements

- [ ] Real-time notifications via WebSockets (Django Channels)
- [ ] Email notifications for important events (swap accepted, new message)
- [ ] Notification preferences per user per event type
- [ ] Notification grouping ("5 new messages from Alice")
- [ ] Push notifications for mobile
- [ ] Cache unread counts with Redis to reduce DB queries
- [ ] Notification expiry — auto-delete old read notifications
- [ ] In-app notification dropdown without visiting the full page