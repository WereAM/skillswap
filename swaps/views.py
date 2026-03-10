from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from skills.models import UserSkill
from swaps.forms import SessionForm, SwapRequestForm
from .models import Session, SwapRequests


# Create your views here.
@login_required
def create_swap(request, skill_id):
    # get the skill requested from another user
    requested_skill = get_object_or_404(UserSkill, pk=skill_id)

    # prevent a user from swapping with themselves
    if requested_skill.user == request.user:
        messages.error(request, "You can't swap with yourself!")
        return redirect('skills:list')
    
    # prevent duplicate pending requests
    existing_request = SwapRequests.objects.filter(
        sender = request.user,
        requested_skill = requested_skill,
        status = 'pending'
    ).exists()

    if existing_request:
        messages.warning(request, "You already have a pending request for this skill!")
        return redirect('skills:detail', pk=skill_id)
    
    if request.method == 'POST':
        # pass the current user to the form to filter their skills
        form = SwapRequestForm(request.user, request.POST)
        if form.is_valid():
            swap = form.save(commit=False)
            swap.sender = request.user
            swap.receiver = requested_skill.user
            swap.requested_skill = requested_skill
            swap.status = 'pending'
            swap.save()
            messages.success(request, "Swap request sent!")
            return redirect('swaps:sent')
    else:
        form = SwapRequestForm(request.user)

    return render(request, 'swaps/create_swap.html', {
        'form': form,
        'requested_skill': requested_skill,
    })

@login_required
def inbox(request):
    # show all swap requests received
    received = SwapRequests.objects.filter(
        receiver = request.user
    ).select_related(
        'sender', 'offered_skill__skill', 'requested_skill__skill'
    ).order_by('-created_at')

    return render(request, 'swaps/inbox.html', {'received': received})

@login_required
def sent_requests(request):
    # show all swap requests sent
    sent = SwapRequests.objects.filter(
        sender = request.user
    ).select_related(
        'receiver', 'offered_skill__skill', 'requested_skill__skill'
    ).order_by('-created_at')

    return render(request, 'swaps/sent_requests.html', {'sent': sent})

@login_required
def swap_detail(request, pk):
    # only a sender or receiver can view details of a swap
    swap = get_object_or_404(SwapRequests, pk=pk)
    if request.user != swap.sender and request.user != swap.receiver:
        messages.error(request, "You do not have permission to view this swap.")
        return redirect('swaps:inbox')
    
    session = None
    session_form = None

    try:
        # check if a session already exists for this swap
        session = swap.session
    except Session.DoesNotExist:
        if swap.status == 'accepted':
            if request.method == 'POST':
                session_form = SessionForm(request.POST)
                if session_form.is_valid():
                    session = session_form.save(commit=False)
                    session.swap_request = swap
                    session.save()
                    messages.success(request, "Session scheduled!")
                    return redirect('swaps:detail', pk=pk)
            else:
                session_form = SessionForm()

    return render(request, 'swaps/swap_detail.html', {
        'swap': swap,
        'session': session,
        'session_form': session_form,
    })

@login_required
def accept_swap(request, pk):
    # only the receiver
    swap = get_object_or_404(SwapRequests, pk=pk, receiver=request.user)

    if swap.status != 'pending':
        messages.error(request, "This request is no longer pending.")
        return redirect('swaps:inbox')
    
    swap.status = 'accepted'
    swap.save()
    messages.success(request, "Swap request accepted!")
    return redirect('swaps:detail', pk=pk)

@login_required
def deny_swap(request, pk):
    # only the receiver
    swap = get_object_or_404(SwapRequests, pk=pk, receiver=request.user)

    if swap.status != 'pending':
        messages.error(request, "This request is no longer pending.")
        return redirect('swaps:inbox')
    
    swap.status = 'rejected'
    swap.save()
    messages.success(request, "Swap request denied!")
    return redirect('swaps:inbox')

@login_required
def cancel_swap(request, pk):
    # only the sender
    swap = get_object_or_404(SwapRequests, pk=pk, sender=request.user)

    if swap.status != 'pending':
        messages.error(request, "Only pending requests can be cancelled.")
        return redirect('swaps:sent')
    
    swap.status = 'cancelled'
    swap.save()
    messages.success(request, "Swap request cancelled!")
    return redirect('swaps:sent')
