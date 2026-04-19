from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from messaging.forms import MessageForm
from .models import Message, Notification
from .utils import create_notification

# Create your views here.
@login_required
def inbox(request):
    """"
    show all of the current users conversations
    group messages by the participant and show the most recent message in each conversation
    """
    
    sent_to = Message.objects.filter(
        sender = request.user
    ).values_list('receiver', flat=True)

    received_from = Message.objects.filter(
        receiver = request.user
    ).values_list('sender', flat=True)

    conversation_user_ids = set(list(sent_to) + list(received_from))

    conversations = []
    for user_id in conversation_user_ids:
        other_user = User.objects.get(pk=user_id)

        latest_message = Message.objects.filter(
            Q(sender = request.user, receiver = other_user) |
            Q(sender = other_user, receiver = request.user)
        ).order_by('-sent_at').first()

        unread_count = Message.objects.filter(
            sender = other_user,
            receiver = request.user,
            is_read = False
        ).count()

        conversations.append({
            'user': other_user,
            'latest_message': latest_message,
            'unread_count': unread_count,
        })

    conversations.sort(
        key = lambda x: x['latest_message'].sent_at,
        reverse=True
    )
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
    })

@login_required
def conversation(request, username):
    """"
    show the full conversation thread
    handle sending of messages
    """

    other_user = get_object_or_404(User, username=username)

    # prevent self messaging
    if other_user == request.user:
        return redirect('messaging:inbox')
    
    chat_messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('sent_at')

    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender=request.user
            message.receiver=other_user
            message.save()

            # notification
            create_notification(
                user=other_user,
                notification_type='new_message',
                content=f'New message from {request.user.username}:'
                        f'{message.content[:50]} {"..." if len(message.content) > 50 else ""}'
            )

            return redirect('messaging:conversation', username=username)
    else:
        form = MessageForm()

    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'chat_messages': chat_messages,
        'form': form,
    })

# show most recent notofications first
@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'messaging/notifications.html', {
        'notifications': user_notifications,
    })

# mark a single notification as read
@login_required
def mark_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect('messaging:notifications')

# mark all notifications as read
def mark_all_read(request):
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)
    return redirect('messaging:notifications')