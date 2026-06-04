from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
import json

from django.conf import settings
from swaps.models import Session, SwapRequests
from .models import SchedulingPreference, AvailabilitySlots
from .forms import EnhancedSessionForm, AvailabilitySlotForm, SchedulingPreferenceForm
from .utils.timezone import get_user_timezone, convert_to_user_timezone
from .utils.conflicts import check_conflict, find_conflicts_in_week
from .utils.suggestions import get_smart_suggestions

@login_required
def calendar_view(request):
    '''
    Main calendar view showing all the user's session per week.
    '''

    # get scheduling preferences/create if first visit
    preferences, _ = SchedulingPreference.objects.get_or_create(user=request.user)
    user_tz_str = preferences.timezone
    user_tz = pytz.timezone(user_tz_str)

    # calculate week range (Monday-Sunday) for the calendar view/navigation
    week_offset = int(request.GET.get('week', 0))
    now_local = datetime.now(user_tz)
    # start of the current week (Monday 00:00) in user's local time, adjusted by week_offset
    week_start_local = now_local - timedelta(days=now_local.weekday())
    week_start_local = week_start_local.replace(hour=0, minute=0, second=0, microsecond=0)
    # apply week offset for navigation
    week_start_local += timedelta(weeks=week_offset)
    week_end_local = week_start_local + timedelta(days=6)
    # convert to UTC for querying sessions
    week_start_utc = week_start_local.astimezone(pytz.UTC)
    week_end_utc = week_end_local.astimezone(pytz.UTC)

    # get all sessions for the user in this week
    user_swap_ids = SwapRequests.objects.filter(
        __import__('django.db.models', fromlist=['Q']).Q(sender=request.user) | 
        __import__('django.db.models', fromlist=['Q']).Q(receiver=request.user),
        status = 'accepted'
    ).values_list('id', flat=True)

    sessions = Session.objects.filter(
        swap_request_id__in=user_swap_ids,
        scheduled_date__range = (week_start_utc, week_end_utc)
    ).select_related('swap_request__sender', 
                     'swap_request__receiver',
                     'swap_request__offered_skill__skill',
                     'swap_request__requested_skill__skill',
                    ).order_by('scheduled_date')
    
    # convert session times to user's local timezone for display
    session_data = []
    for session in sessions:
        local_dt = convert_to_user_timezone(session.scheduled_date, user_tz_str)
        other_user = (
            session.swap_request.receiver
            if session.swap_request.sender == request.user
            else session.swap_request.sender
        )
        session_data.append({
            'session': session,
            'local_dt': local_dt,
            'other_user': other_user,
            'skill_name': session.swap_request.offered_skill.skill.name,
            'day_index': local_dt.weekday(),
            'hour': local_dt.hour,
            'minute': local_dt.minute,
            # position on the calendar grid can be calculated as the position from the top of the hour block
            'top_position': (local_dt.minute / 60) * 100,  # percentage from the 0 minute mark
            'height_position': (session.duration_minutes / 60) * 100,  # percentage of the hour block
        })

    # calendar header showing the days of the week with dates
    week_days = []
    for i in range(7):
        day = week_start_local + timedelta(days=i)
        week_days.append({
            'date': day,
            'day_name': day.strftime('%a').upper(),
            'day_num': day.day,
            'is_today': day.date() == now_local.date(),
        })

    # upcoming sessions for the sidebar (next 3)
    upcoming =Session.objects.filter(
        swap_request_id__in=user_swap_ids,
        scheduled_date__gte=timezone.now(),
        status='scheduled'
    ).select_related(
        'swap_request__offered_skill__skill',
        'swap_request__sender',
        'swap_request__receiver',
    ).order_by('scheduled_date')[:3]

    upcoming_data = []
    for session in upcoming:
        local_dt = convert_to_user_timezone(session.scheduled_date, user_tz_str)
        other_user = (
            session.swap_request.receiver
            if session.swap_request.sender == request.user
            else session.swap_request.sender
        )
        upcoming_data.append({
            'session': session,
            'local_dt': local_dt,
            'other_user': other_user,
            'skill_name': session.swap_request.offered_skill.skill.name,
        })

    # find any conflicts in this week to show a warning in the UI
    conflicts = find_conflicts_in_week(request.user, week_start_utc)

    return render(request, 'scheduling/calendar.html', {
        'sessions': session_data,
        'week_days': week_days,
        'week_start': week_start_local,
        'week_end': week_end_local,
        'week_offset': week_offset,
        'upcoming': upcoming_data,
        'conflicts': conflicts,
        'user_timezone': user_tz_str,
        'hours': range(24),
    })

@login_required
def schedule_session(request, swap_pk):
    '''
    Enhanced session scheduling with smart suggestions,
    real-time conflict checking, timezone handling, and map location.
    '''
    
    swap = get_object_or_404(SwapRequests, pk=swap_pk, status='accepted')

    # security check to ensure the user is part of this swap
    if request.user != swap.sender and request.user != swap.receiver:
        messages.error(request, 'You are not authorized to schedule this session.')
        return redirect('swaps:inbox')
    
    preferences, _ = SchedulingPreference.objects.get_or_create(user=request.user)
    other_user = swap.receiver if request.user == swap.sender else swap.sender

    # smart suggestions
    suggestions = get_smart_suggestions(
        sender = request.user, 
        receiver = other_user,
        duration_minutes = 60,
        num_suggestions = 5
    )

    # convert suggestions to user's local timezone for display
    user_tz_str = preferences.timezone
    suggestions_local = [
        convert_to_user_timezone(s, user_tz_str) for s in suggestions
    ]

    if request.method == 'POST':
        form = EnhancedSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.swap_request = swap

            # convert submitted datetime from user's local timezone to UTC before saving
            raw_datetime = form.cleaned_data['scheduled_date']
            user_tz = pytz.timezone(user_tz_str)
            if timezone.is_naive(raw_datetime):
                raw_datetime = user_tz.localize(raw_datetime)
            session.scheduled_date = raw_datetime.astimezone(pytz.UTC)

            # check for conflicts before saving
            conflict = check_conflict(
                request.user,
                session.scheduled_date,
                session.duration_minutes,
                preferences.buffer_minutes
            )
            if conflict['has_conflict']:
                messages.warning(
                    request, 
                    f'This time conflicts with an existing session.'
                    f'Please choose a different time.'
                )
                return render(request, 'scheduling/schedule_session.html', {
                    'form': form,
                    'swap': swap,
                    'suggestions': suggestions_local,
                    'conflict': conflict,
                    'other_user': other_user,
                    'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
                })
            
            session.save()

            # create google calendar event
            from .utils.google_calendar import create_google_calendar_event
            create_google_calendar_event(session, swap.sender, swap.receiver)

            # create notifications for both participants
            from messaging.utils import create_notification
            create_notification(
                user = other_user,
                notification_type = 'session_scheduled',
                content=f'{request.user.username} scheduled your session for '
                        f'{convert_to_user_timezone(session.scheduled_date, user_tz_str).strftime("%A, %d %b at %H:%M")}.'
            )

            messages.success(request, 'Session scheduled successfully!')
            return redirect('scheduling:calendar')
    else:
        # prefill timezone with user's preference
        form = EnhancedSessionForm(initial={'timezone': user_tz_str})

    return render(request, 'scheduling/schedule_session.html', {
        'form': form,
        'swap': swap,
        'suggestions': suggestions_local,
        'other_user': other_user,
        'user_timezone': user_tz_str,
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    })

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
            return redirect('scheduling:availability')
        
        elif action == 'add_slot':
            slot_form = AvailabilitySlotForm(request.POST)
            if slot_form.is_valid():
                slot = slot_form.save(commit=False)
                slot.user = request.user
                slot.save()
                messages.success(request, 'Availability slot added!')
            return redirect('scheduling:availability')
        
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
def api_set_timezone(request):
    """Auto-saves user's detected browser timezone"""
    if request.method == 'POST':
        import json
        import pytz
        data = json.loads(request.body)
        tz = data.get('timezone', 'UTC')
        # Validate it's a real timezone
        if tz in pytz.all_timezones:
            preferences, _ = SchedulingPreference.objects.get_or_create(user=request.user)
            preferences.timezone = tz
            preferences.save()
            return JsonResponse({'status': 'ok', 'timezone': tz})
    return JsonResponse({'status': 'error'}, status=400)

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