import json
from datetime import timedelta
from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from requests import session

def get_google_calendar_service(user):
    '''
    Builds an authenticated Google Calendar API service for a user.
    Requires the user to have connected their Google Calendar.
    Returns a Google Calendar service object or None if the user has not connected their calendar.
    '''
    try:
        token_json = user.scheduling_preferences.google_calendar_token
        if not token_json:
            return None  # User has not connected their Google Calendar
        token_data = json.loads(token_json)
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        return build('calendar', 'v3', credentials=credentials)
    except Exception:
        return None  # In case of any error, treat as not connected

def create_google_calendar_event(session, sender, receiver):
    '''
    Called when a session is scheduled.
    Creates a Google Calendar event for both participants.
    Args: - session: Session model instance
        - sender: User object initiating the swap
        - receiver: User object receiving the swap request
    Returns: event ID string if event created successfully, else None
    '''
    service = get_google_calendar_service(sender)
    if not service:
        return None  # Sender has not connected their calendar
    
    event_end = session.scheduled_date + timedelta(minutes=session.duration_minutes)
    event_body = {
        'summary': f'SkillSwap: {session.swap_request.offered_skill.skill.name} ⇄ {session.swap_request.requested_skill.skill.name}',
        'description': f'SkillSwap session\n\nOfferring: {session.swap_request.offered_skill.skill.name}\nRequesting: {session.swap_request.requested_skill.skill.name}\n\nNotes:{session.notes}',
        'start': {
            'dateTime': session.scheduled_date.isoformat(),
            'timeZone': session.timezone or 'UTC',
        },
        'end': {
            'dateTime': event_end.isoformat(),
            'timeZone': session.timezone or 'UTC',
        },
        'attendees': [
            {'email': sender.email},
            {'email': receiver.email},
        ],
        'conferenceData': {
            'createRequest': {'requestId': f'skillswap-{session.pk}'}
        } if not session.meeting_link else None,
    }

    # if physical meeting
    if session.location_name:
        event_body['location'] = session.location_name

    # if virtual meeting
    if session.meeting_link:
        event_body['description'] += f'\n\nMeeting Link: {session.meeting_link}'

    try:
        event = service.events().insert(
            calendarId='primary',
            body=event_body,
            sendUpdates='all'  # send email invites to attendees
        ).execute()

        # store the event ID in the session for future reference (e.g. updates/cancellations)
        session.google_calendar_event_id = event.get('id', '')
        session.save()

        return event.get('id')
    except HttpError as e:
        print(f"Error creating Google Calendar event: {e}")
        return None  # Handle any errors gracefully
    
def update_google_calendar_event(session):
    '''
    Updates an existing Google Calendar event when session details change (e.g. rescheduling).
    '''
    if not session.google_calendar_event_id:
        return False  # No event to update
    
    service = get_google_calendar_service(session.swap_request.sender)
    if not service:
        return False  # Sender has not connected their calendar
    
    event_end = session.scheduled_date + timedelta(minutes=session.duration_minutes)

    try:
        event = service.events().get(
            calendarId='primary',
            eventId=session.google_calendar_event_id
        ).execute()

        event['start']['dateTime'] = session.scheduled_date.isoformat()
        event['end']['dateTime'] = event_end.isoformat()
        if session.location_name:
            event['location'] = session.location_name

        service.events().update(
            calendarId='primary',
            eventId=session.google_calendar_event_id,
            body=event,
            sendUpdates='all'
        ).execute()
        return True
    except HttpError as e:
        print(f"Error updating Google Calendar event: {e}")
        return False 
    
def delete_google_calendar_event(session):
    '''
    Deletes a Google Calendar event when a session is cancelled.
    '''
    if not session.google_calendar_event_id:
        return False  # No event to delete
    
    service = get_google_calendar_service(session.swap_request.sender)
    if not service:
        return False  # Sender has not connected their calendar
    
    try:
        service.events().delete(
            calendarId='primary',
            eventId=session.google_calendar_event_id,
            sendUpdates='all',
        ).execute()
        return True
    except HttpError as e:
        print(f"Error deleting Google Calendar event: {e}")
        return False