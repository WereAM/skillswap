from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from messaging.forms import MessageForm
from .models import Message

# Create your views here.
@login_required
def inbox(request):
    """"
    show all of the current users conversations
    group messages by the participant and show the most recent message in each conversation
    """
    
    sent_to = Message.object.filter(
        sender = request.user
    ).values_list('receiver', flat=True)

    received_from = Message.object.filter(
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
    
    messages = Message.objects.filter(
        Q(sender = request.user, receiver = other_user) |
        Q(sender = other_user, receiver = request.user)
    ).order_by('sent_at')

    Message.objects.filter(
        sender = other_user,
        receiver = request.user,
        is_read = False
    ).update(is_read = True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit = False)
            message.sender = request.sender
            message.receiver = other_user
            message.save()
            return redirect('messaging:convesration', username=username)
    else:
        form = MessageForm()

    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'messages': messages,
        'form': form,
    })