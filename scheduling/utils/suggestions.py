from datetime import datetime, timedelta, time
import pytz
from .conflicts import check_conflict
from .timezone import convert_to_utc

'''
Finds mutually available time slots for two users
Algorithm:
    1. Define the date range to check (e.g. next 7 days)
    2. Get all available time slots for each user within that range
    3. Find overlapping windows between the two users
    4. Check for conflicts within each overlapping window
    5. Returns the best suggestions sorted by earliest available time

Args:
    - sender: User object initiating the swap
    - receiver: User object receiving the swap request
    - duration_minutes: int, duration of the session in minutes
    - num_suggestions: int, number of suggestion options to return

Returns:
    - list of datetime objects representing suggested session start times in UTC
'''

def get_smart_suggestions(sender, receiver, duration_minutes=60, num_suggestions=5):
    try:
        sender_preferences = sender.scheduling_preferences
        receiver_preferences = receiver.scheduling_preferences
        sender_timezone = sender_preferences.timezone
        receiver_timezone = receiver_preferences.timezone
        sender_buffer = sender_preferences.buffer_minutes
        receiver_buffer = receiver_preferences.buffer_minutes
        buffer = max(sender_buffer, receiver_buffer)
    except Exception:
        # If preferences are not set, use defaults
        sender_timezone = 'UTC'
        receiver_timezone = 'UTC'
        buffer = 15

    sender_slots = sender.availability_slots.filter(is_active=True)
    receiver_slots = receiver.availability_slots.filter(is_active=True)

    if not sender_slots.exists() or not receiver_slots.exists():
        # fall back to business hours if no availability is set
        return get_business_hours_suggestions(
            sender, receiver, duration_minutes, buffer, num_suggestions
        )
    
    suggestions = []
    # look ahead 2 weeks for available slots
    now = datetime.now(pytz.utc)
    check_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    for day_offset in range(14):
        check_date = now + timedelta(days=day_offset)
        day_of_week = check_date.weekday()  # 0=Monday, 6=Sunday

        # find sender slots for this day
        sender_day_slots = sender_slots.filter(day_of_week=day_of_week)
        receiver_day_slots = receiver_slots.filter(day_of_week=day_of_week)

        for sender_slot in sender_day_slots:
            for receiver_slot in receiver_day_slots:
                # find overlapping time between the 2 availability windows
                overlap_start = max(sender_slot.start_time, receiver_slot.start_time)
                overlap_end = min(sender_slot.end_time, receiver_slot.end_time)

                if overlap_end <= overlap_start:
                    continue  # no overlap

                # convert overlap times to UTC datetimes
                s_tz = pytz.timezone(sender_timezone)
                slot_start_naive = datetime.combine(check_date.date(), overlap_start)
                slot_end_naive = datetime.combine(check_date.date(), overlap_end)
                slot_start_utc = s_tz.localize(slot_start_naive).astimezone(pytz.utc)
                slot_end_utc = s_tz.localize(slot_end_naive).astimezone(pytz.utc)

                # step through the overlaps in session-sized chunks
                candidate = slot_start_utc
                while candidate + timedelta(minutes=duration_minutes) <= slot_end_utc:
                    # check both users have no conflicts at this candidate time
                    sender_free = not check_conflict(sender, candidate, duration_minutes, buffer)['has_conflict']
                    receiver_free = not check_conflict(receiver, candidate, duration_minutes, buffer)['has_conflict']

                    if sender_free and receiver_free:
                        suggestions.append(candidate)

                    if len(suggestions) >= num_suggestions:
                        return sorted(suggestions)[:num_suggestions]
                    
                    candidate += timedelta(minutes=30)  # check every 30 minutes

    return sorted(suggestions)[:num_suggestions]
            
'''
Fallback method to suggest times based on business hours (9am-5pm)
if no availability preferences are set by either user.
'''
def get_business_hours_suggestions(sender, receiver, duration_minutes, buffer, num_suggestions):
    suggestions = []
    now = datetime.now(pytz.utc)

    for day_offset in range(1, 14):
        candidate_date = now + timedelta(days=day_offset)
        if candidate_date.weekday() >= 5:  # skip weekends
            continue

        for hour in range(9, 17 - (duration_minutes // 60)):
            candidate = candidate_date.replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            sender_free = not check_conflict(sender, candidate, duration_minutes, buffer)['has_conflict']
            receiver_free = not check_conflict(receiver, candidate, duration_minutes, buffer)['has_conflict']

            if sender_free and receiver_free:
                suggestions.append(candidate)

            if len(suggestions) >= num_suggestions:
                return sorted(suggestions)[:num_suggestions]
            
    return sorted(suggestions)[:num_suggestions]
            