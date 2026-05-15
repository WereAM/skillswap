import pytz
from datetime import datetime
from django.utils import timezone

'''
Convert a UTC datetime to the user's local timezone.
Args: - dt: datetime object in UTC
      - user_timezone: string representing the user's timezone, e.g. 'Europe/London
Returns: timezone-aware datetime object in the user's local timezone
'''
def convert_to_user_timezone(dt, user_timezone):
    if not dt:
        return dt
    
    try:
        user_tz = pytz.timezone(user_timezone)
        if timezone.is_naive(dt):
            dt = pytz.utc.localize(dt)
        return dt.astimezone(user_tz)
    except pytz.exceptions.UnknownTimeZoneError:
        return dt

'''
Convert a user's local timezone to UTC for database storage.
Args: - dt: naive datetime object in the user's local timezone
      - user_timezone: string representing the user's timezone, e.g. 'Europe/London'
Returns: datetime object in UTC
'''
def convert_to_utc(dt, user_timezone):
    try:
        user_tz = pytz.timezone(user_timezone)
        if timezone.is_naive(dt):
            dt = user_tz.localize(dt)
        return dt.astimezone(pytz.utc)
    except pytz.exceptions.UnknownTimeZoneError:
        return dt
    
'''
Get user's prederred timezone.
Use UTC if no preference set or invalid timezone.
'''
def get_user_timezone(user):
    try:
        return user.scheduling_preference.timezone
    except (AttributeError, pytz.exceptions.UnknownTimeZoneError):
        return 'UTC'
    
'''
Format a datetime object for display in the user's local timezone.
'''
def format_datetime_for_user(dt, user_timezone, fmt='%A, %d %B %Y at %H %M'):
    local_dt = convert_to_user_timezone(dt, user_timezone)
    return local_dt.strftime(fmt) if local_dt else ''