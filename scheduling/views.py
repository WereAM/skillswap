from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
import json

from swaps.models import Session, SwapRequests
from .models import SchedulingPreference, AvailabilitySlots
from .forms import EnhancedSessionForm, AvailabilitySlotForm, SchedulingPreferenceForm
from .utils.timezone import get_user_timezone, convert_to_user_timezone
from .utils.conflicts import check_conflict, find_conflicts_in_week
from .utils.suggestions import get_smart_suggestions

@login_required
def set_availability(request):
    '''
    Lets users set their weekly recurring availability and scheduling preferences
    '''

    preferences, _ = SchedulingPreference.objects.get_or_create(user=request.user)
    slots = AvailabilitySlots.objects.filter(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_preferences':
            preferences_form = SchedulingPreferenceForm(request.POST, instance=preferences)
            if preferences_form.is_valid():
                preferences_form.save()
                messages.success(request, 'Scheduling preferences saved!')
            return redirect('set_availability')
        
        elif action == 'add_slot':
            slot_form = AvailabilitySlotForm(request.POST)
            if slot_form.is_valid():
                slot = slot_form.save(commit=False)
                slot.user = request.user
                slot.save()
                messages.success(request, 'Availability slot added!')
            return redirect('set_availability')
        
        elif action == 'delete_slot':
            slot_id = request.POST.get('slot_id')
            AvailabilitySlots.objects.filter(pk=slot_id, user=request.user).delete()
            messages.success(request, 'Slot removed')
            return redirect('scheduling:availability')
        
    return render(request, 'scheduling/availability.html', {
        'preferences': preferences,
        'preferences_form': SchedulingPreferenceForm(instance=preferences),
        'slot_form': AvailabilitySlotForm(),
        'slots': slots,
    })

@login_required
def api_check_conflict(request):
    '''
    AJAX endpoint for real time conflict checking when users select a date/time for scheduling.
    Called from the schedule session form's datetime picker.
    Returns JSON  used to show the conflict warning in the UI instantly.
    '''
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        datetime_str = data.get('datetime')
        duration = int(data.get('duration', 60))
        user_tz = data.get('timezone', 'UTC')

        # parse and convert to UTC
        datetime_naive = datetime.fromisoformat(datetime_str)
        tz = pytz.timezone(user_tz)
        datetime_utc = tz.localize(datetime_naive).astimezone(pytz.UTC)

        preferences, _ = SchedulingPreference.objects.get_or_create(user=request.user)
        result = check_conflict(request.user, datetime_utc, duration, preferences.buffer_minutes)

        return JsonResponse({
            'has_conflict': result['has_conflict'],
            'message': (
                f'This time conflicts with an existing session at '
                f'{convert_to_user_timezone(result["conflict_start"], user_tz).strftime("%H:%M")}'
                if result['has_conflict'] else 'This time slot is available.'
            )
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def api_get_suggestions(request):
    '''
    AJAX endpoint returning smart scheduling suggestions.
    Called when the schedule session page loads.
    '''

    swap_pk = request.GET.get('swap_pk')
    if not swap_pk:
        return JsonResponse({'error': 'Missing swap_pk parameter'}, status=400)
    
    swap = get_object_or_404(SwapRequests, pk=swap_pk)
    other_user = swap.requester if swap.receiver != request.user else swap.sender
    preferences, _ = SchedulingPreference.objects.get_or_create(user=request.user)

    suggestions = get_smart_suggestions(request.user, other_user)
    user_tz_str = preferences.timezone

    return JsonResponse({
        'suggestions': [
            {
                'utc': s.isoformat(),
                'local': convert_to_user_timezone(s, user_tz_str).strftime('%A, %d, %b at %H:%M'),
            }
            for s in suggestions
        ]
    })