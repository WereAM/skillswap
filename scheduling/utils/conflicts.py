from datetime import timedelta
from swaps.models import Session, SwapRequests
from django.db.models import Q

def get_user_sessions(user, start_date, end_date):
    '''
    Gets all scheduled sessions for a user within a date range.
    '''
    swap_ids = SwapRequests.objects.filter(
        Q(sender=user) | Q(receiver=user),
        status = 'accepted'
    ).values_list('id', flat=True)

    return Session.objects.filter(
        swap_request_id__in=swap_ids,
        status='scheduled',
        scheduled_date__range=(start_date, end_date)
    ).order_by('scheduled_date')

def check_conflict(user, proposed_start, duration_minutes, buffer_minutes=15, exclude_session_id=None):
    '''
    Checks if a poposed session time conflicts with any existing sessions for the user.
    Includes the uffer time before and after each session.
    Args: - user: User object
        - proposed_start: UTC datetime object for proposed session start time
        - duration_minutes: int, duration of the proposed session in minutes
        - buffer_minutes: int, number of minutes to buffer before and after each session
        - exclude_session_id: int, session ID to exclude from conflict check (e.g. when rescheduling)
    Returns: dict with 'has_conflict' bool and 'conflicting_session' if found
    '''
    proposed_end = proposed_start + timedelta(minutes=duration_minutes)
    buffered_start = proposed_start - timedelta(minutes=buffer_minutes)
    buffered_end = proposed_end + timedelta(minutes=buffer_minutes)

    # get all swaps involving the user
    user_swap_ids = SwapRequests.objects.filter(
        Q(sender=user) | Q(receiver=user),
        status='accepted'
    ).values_list('id', flat=True)

    # find any sessions that overlap with the proposed time (including buffer)
    existing_sessions = Session.objects.filter(
        swap_request_id__in=user_swap_ids,
        status='scheduled'
    )

    if exclude_session_id:
        existing_sessions = existing_sessions.exclude(pk=exclude_session_id)

    for session in existing_sessions:
        session_end = session.scheduled_date + timedelta(minutes=session.duration_minutes)
        # check for overlap: session starts before buffered end and ends after buffered start
        if buffered_start < session_end and buffered_end > session.scheduled_date:
            return {
                'has_conflict': True,
                'conflicting_session': session,
                'conflict_start': session.scheduled_date,
                'conflict_end': session_end,
            }
        
    return {'has_conflict': False, 'conflicting_session': None}

def find_conflicts_in_week(user, week_start):
    '''
    Finds all conflicting sessions for a user within a week starting from the given date.
    '''
    week_end = week_start + timedelta(days=6)
    sessions = get_user_sessions(user, week_start, week_end)
    conflicts = []

    session_list = list(sessions)
    for i in range(len(session_list) -1):
        current_session = session_list[i]
        next_session = session_list[i + 1]
        current_end = current_session.scheduled_date + timedelta(minutes=current_session.duration_minutes)
        if current_end > next_session.scheduled_date:
            conflicts.append((current_session, next_session))
    
    return conflicts