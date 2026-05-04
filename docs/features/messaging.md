# Messaging

## Overview

SkillSwap includes a direct messaging system allowing any two users to communicate privately. Messages are not tied to a specific swap. They're standalone conversations between users. This allows people to ask questions before requesting a swap, coordinate session details, or simply stay in touch after a successful exchange.

## How it Works

### Starting a Conversation

```
User visits another user's public profile
    → clicks "Send Message"
        → redirected to /messaging/<username>/
            → conversation thread loads (empty if first contact)
                → user types and submits message
                    → message saved
                        → receiver gets notification
                            → page reloads showing sent message
```

### Reading Messages

```
User visits /messaging/
    → inbox loads showing all conversations
        → each conversation shows latest message preview
            → unread conversations highlighted with border
                → unread count badge shown in navbar
                    → user clicks a conversation
                        → thread loads
                            → all unread messages marked as read
                                → unread count updates
```

## Technical Implementation

### Model (`messaging/models.py`)

**`Message`**

```python
class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages'
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
```

Messages are simple and flat, there's no thread or conversation object. Conversations are derived by querying all messages between two specific users.

### Views (`messaging/views.py`)

**`inbox`**
Builds conversation previews by finding all users the current user has exchanged messages with, then fetching the latest message and unread count for each:

```python
# Get all users involved in conversations
sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
conversation_user_ids = set(list(sent_to) + list(received_from))

# Build preview for each conversation
for user_id in conversation_user_ids:
    other_user = User.objects.get(pk=user_id)
    latest_message = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('-sent_at').first()

    unread_count = Message.objects.filter(
        sender=other_user, receiver=request.user, is_read=False
    ).count()
```

**`conversation`**
Fetches the full message thread between two users and marks unread messages as read in a single query:

```python
# Fetch all messages between the two users chronologically
chat_messages = Message.objects.filter(
    Q(sender=request.user, receiver=other_user) |
    Q(sender=other_user, receiver=request.user)
).order_by('sent_at')

# Mark all unread messages from other user as read in one DB call
Message.objects.filter(
    sender=other_user, receiver=request.user, is_read=False
).update(is_read=True)
```

Using `.update()` instead of looping and saving each message individually is significantly more efficient for large conversations.

### Form (`messaging/forms.py`)

**`MessageForm`**
Simple single-field form for message content with no label for cleaner UI:

```python
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }
        labels = {'content': ''}  # Hide label for chat UI feel
```

### Context Processor (`accounts/context_processors.py`)

The unread message count is injected into every template automatically:

```python
def unread_messages(request):
    if request.user.is_authenticated:
        unread_msg_count = Message.objects.filter(
            receiver=request.user, is_read=False
        ).count()
        return {'unread_messages_count': unread_msg_count}
    return {'unread_messages_count': 0}
```

This runs on every request, so the navbar badge always shows the current count without any view needing to pass it explicitly.

### Auto-Scroll JavaScript

The conversation template includes a small script to scroll to the latest message on load:

```javascript
const thread = document.getElementById('message-thread');
if (thread) {
    thread.scrollTop = thread.scrollHeight;
}
```

### Post/Redirect/Get Pattern

After sending a message, the view redirects back to the conversation page:

```python
message.save()
return redirect('messaging:conversation', username=username)
```

This prevents the browser from resubmitting the form on page refresh (which would duplicate the message).

## URLs

| URL | Name | Auth Needed | Description |
|---|---|---|---|
| `/messaging/` | `messaging:inbox` | Yes | Message inbox |
| `/messaging/<username>/` | `messaging:conversation` | Yes | Conversation thread |

## UI Design

### Chat Bubbles

Messages are displayed as chat bubbles aligned by sender:

```
Own messages → right-aligned, teal background
Other's messages → left-aligned, light grey background
```

Read receipts shown on sent messages:
- `✓` — sent
- `✓✓` — read by receiver

### Inbox Preview

Each conversation in the inbox shows:
- Avatar placeholder (first letter of username)
- Full name or username
- Latest message preview (truncated to 10 words)
- "You: " prefix if the latest message was sent by the current user
- Unread count badge
- Date of latest message

Unread conversations have a teal left border to draw attention.

## Key Design Decisions

### Why no thread/conversation model?
Adding a `Conversation` model would require creating it before the first message, then associating all messages with it. For a simple 1-to-1 messaging system this adds complexity without benefit. Conversations are derived from message queries which is simpler and equally effective at this scale.

### Why `.update()` for marking messages as read?
Looping through messages and calling `.save()` on each triggers a separate database query per message. `.update()` marks all of them read in a single SQL UPDATE statement, which is much more efficient especially for long conversations.

### Why use `chat_messages` not `messages` as context variable?
`messages` is a reserved variable name in Django templates — it's used by the messages framework for flash notifications. Using it as a queryset variable would silently break flash messages throughout the page.

### Why redirect after send (Post/Redirect/Get)?
Without the redirect, pressing browser refresh would resubmit the form and send a duplicate message. The PRG pattern prevents this by turning the POST into a GET after a successful send.

## Known Limitations

- No real-time updates - page must be refreshed to see new messages
- No message deletion
- No typing indicators
- No media/file sharing in messages
- Inbox query is not optimised for very large numbers of conversations
- No conversation archiving

## Future Improvements

- [ ] WebSocket-based real-time messaging (Django Channels)
- [ ] Typing indicators
- [ ] Message deletion
- [ ] Image and file sharing
- [ ] Message search
- [ ] Conversation archiving
- [ ] Push notifications for new messages
- [ ] Message reactions (emoji)
- [ ] Optimise inbox query with annotation-based approach