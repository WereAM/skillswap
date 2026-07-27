from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
import pytz

from scheduling.models import AvailabilitySlots, SchedulingPreference,  APIClient
from scheduling.utils.suggestions import get_smart_suggestions
from scheduling.utils.conflicts import check_conflict
from scheduling.utils.timezone import convert_to_user_timezone, get_user_timezone
from .serializers import (
    AvailabilitySlotsSerializer,
    AvailabilitySlotCreateSerializer,
    TimeSuggestionSerializer,
    ConflictCheckSerializer,
    SessionSerializer,
    APIClientSerializer,
)
from .authentication import APIKeyAuthentication


# AUTHENTICATION ENDPOINTS
class ObtainTokenView(APIView):
    """
    POST /chronogami/v1/auth/token/
    Exchange username and password for JWT access amd refresh tokens.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary= "Obtain JWT tokens",
        description="Exchange credentials for access and refresh tokens.",
        responses= {200: {
                    'type': 'object',
                    'properties': {
                        'access': {'type': 'string'},
                        'refresh': {'type': 'string'},
                        'user_id': {'type': 'integer'},
                        'username':{'type': 'string'},
                    }
                }}
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'username and password are required'},
                status= status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status= status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'username': user.username,
        })
    
class RegisterAPIClientView(APIView):
    """
    POST /chronogami/v1/auth/register-client/
    Register as an API client and receive an API key.
    Requires JWT auth.
    API keys are passed in the X-API-Key header for subsequent requests.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary = "Register API client",
        description= "Creates a new API client and returns your API key. STORE IT SECURELY! It will not be shown again.",
    )

    def post(self, request):
        serializer = APIClientSerializer(data=request.data)
        if serializer.is_valid():
            client = serializer.save(owner=request.user)
            return Response(
                {
                    'message': "API client registered successfully.",
                    'api_key': client.api_key,
                    'warning': "Store this securely, it will not be shown again!",
                    'client': APIClientSerializer(client).data,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# SCHEDULING ENDPOINTS
class SuggestTimesView(APIView):
    """
    POST /chronogami/v1/scheduling/suggest/
    Returns smart time suggestions for two users.
    Authenticate with JWT Bearer token or X-API-Key header.
    """

    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary= "Get smart time suggestions.",
        description=(
            "Finds mutually available time slots for two users. "
            "Results are returned in UTC - convert to local time zone using the provided time zone strings."
        ),
        request=TimeSuggestionSerializer,
        responses={200: {
            'type': 'object',
            'properties': {
                'suggestions': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'utc': {'type': 'string', 'format': 'date-time'},
                            'user_a_local': {'type': 'string'},
                            'user_b_local': {'type': 'string'},
                            'day': {'type': 'string'},
                        }
                    }
                },
                'user_a_timezone': {'type': 'string'},
                'user_b_timezone': {'type': 'string'},
                'count': {'type': 'integer'},
            }
        }},
        examples=[
            OpenApiExample(
                'Request',
                value={
                    'user_a_id': 1,
                    'user_b_id': 2,
                    'duration_minutes': 60,
                    'num_suggestions': 5
                }
            )
        ]
    )

    def post(self, request):
        serializer = TimeSuggestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data

        # validate users exist
        try:
            user_a = User.objects.get(pk=data['user_a_id'])
            user_b = User.objects.get(pk=data['user_b_id'])
        except User.DoesNotExist:
            return Response(
                {'error': 'One or both user IDs not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # get suggestions
        suggestions = get_smart_suggestions(
            sender=user_a,
            receiver=user_b,
            duration_minutes=data['duration_minutes'],
            num_suggestions=data['num_suggestions'],
        )

        # get both users' timezones for display
        tz_a = get_user_timezone(user_a)
        tz_b = get_user_timezone(user_b)

        # format response with times in both users' timezones
        formatted = []
        for s in suggestions:
            local_a = convert_to_user_timezone(s, tz_a)
            local_b = convert_to_user_timezone(s, tz_b)
            formatted.append({
                'utc': s.isoformat(),
                'user_a_local': local_a.strftime('%A, %d %b %Y at %H:%M %Z'),
                'user_b_local': local_b.strftime('%A, %d %b %Y at %H:%M %Z'),
                'day': s.strftime('%A'),
                'timestamp': int(s.timestamp()),
            })

        return Response({
            'suggestion': formatted,
            'user_a_timezone': tz_a,
            'user_b_timezone': tz_b,
            'duration_minnutes': data['duration_minutes'],
            'count': len(formatted),
        })

class ConflictCheckView(APIView):
    """
    POST /chronogami/v1/scheduling/conflicts/
    Checks if a proposed time slot conflicts with a user's existing sessions.
    Includes buffer time.
    """

    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary= "Check for scheduling conflicts.",
        description= "Returns whether a proposed time conflicts with existing sessions, including buffer time.",
        request=ConflictCheckSerializer,
    )

    def post(self, request):
        serializer = ConflictCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data

        try:
            user = User.objects.get(pk=data['user_id'])
        except User.DoesNotExist:
            return Response({'error': "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        prefs, _ = SchedulingPreference.objects.get_or_create(user=user)

        result = check_conflict(
            user=user,
            proposed_start=data['proposed_datetime'],
            duration_minutes=data['duration_minutes'],
            buffer_minutes=prefs.buffer_minutes,
        )

        response_data = {
            'has_conflict': result['has_conflict'],
            'user_id': user.id,
            'proposed_start': data['proposed_datetime'].isoformat(),
            'duration_minutes': data['duration_minutes'],
            'buffer_minutes': prefs.buffer_minutes,
        }

        if result['has_conflict'] and result['conflicting_session']:
            session = result['conflicting_session']
            response_data['conflict'] = {
                'session_id': session.pk,
                'conflict_start': result['conflict_start'].isoformat(),
                'conflict_end': result['conflict_end'].isoformat(),
                'message': f'Conflicts with an existing session at {result["conflict_start"].strftime("%H:%M UTC")}',
            }

        return Response(response_data)

class AvailabilityView(APIView):
    """
    GET /chronogami/v1/scheduling/availability/<user_id>    # returns a user's weekly availability slots
    POST /chronogami/v1/scheduling/availability/<user_id>   # adds a new availability slot for the authenticated user
    """

    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary= "Get user's availability",
        description= "Returns all weekly availablity slots for a user.",
    )

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': "User not found"}, status= status.HTTP_404_NOT_FOUND)

        slots = AvailabilitySlots.objects.filter(user=user, is_active=True)
        prefs, _ = SchedulingPreference.objects.get_or_create(user=user)

        return Response({
            "user_id": user.id,
            "username": user.username,
            "timezone": prefs.timezone,
            "slots": AvailabilitySlotsSerializer(slots, many=True).data,
        })

    @extend_schema(
        summary= "Add availability slot",
        description= "Adds a new recurring weekly availability slot for the authenticated user.",
        request= AvailabilitySlotCreateSerializer,
    )

    def post(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {'error': "You can only manage your own availability."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AvailabilitySlotCreateSerializer(data=request.data)
        if serializer.is_valid():
            slot = serializer.save(user = request.user)
            return Response(
                AvailabilitySlotsSerializer(slot).data,
                status=status.HTTP_201_CREATED
            )     
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

class UserSessionsView(APIView):
    """
    GET /chronogami/v1/scheduling/sessions/<user_id>/
    Returns all scheduled sessions for a user.
    Filter by status=scheduled/completed/cancelled
    """

    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary = "Get user's scheduled sessions",
        parameters = [
            OpenApiParameter('status', description= "Filter by status", required=False), 
            OpenApiParameter('from_date', description= "Filter from date (ISO 8601)", required=False), 
            OpenApiParameter('to_date', description= "Filter to date (ISO 8601)", required=False), 
        ]
    )

    def get(self, request, user_id):
        from django.db.models import Q
        from swaps.models import SwapRequests

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id != user_id:
            return Response(
                {'error': "You can only view your own sessions"},
                status= status.HTTP_403_FORBIDDEN
            )

        # get all swaps the user is part of
        swap_ids = SwapRequests.objects.filter(
            Q(sender=user) | Q(receiver=user),
            status='accepted'
        ).values_liat('id', flat=True)

        from swaps.models import Session
        sessions = Session.objects.filter(
            swap_request_id__in = swap_ids
        ).select_related(
            'swap_request__sender',
            'swap_request__receiver',
            'swap_request__offered_skill__skill',
        ).order_by('scheduled_date')

        # filters
        status_filter = request.query_params.get('status')
        if status_filter:
            sessions = sessions.filter(status_filter)

        from_date = request.query_params.get('from_date')
        if from_date:
            sessions = sessions.filter(from_date)

        to_date = request.query_params.get('to_date')
        if to_date:
            sessions = sessions.filter(to_date)

        # get user time zone to display
        tz = get_user_timezone(user)

        return Response({
            "user_id": user.id,
            "username": user.username,
            "timezone": tz,
            "count": sessions.count(),
            "sessions": SessionSerializer(sessions, many=True).data,
        })

class TimezoneListView(APIView):
    """
    GET /chronogami/v1/scheduling/timezones/
    Returns all valid IANA timezone strings.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary= "List all timezones",
        description= "Returns all valid IANA timezone strings grouped by region."
    )

    def get(self, request):
        # group by region
        grouped = {}
        for tz in pytz.common_timezones:
            region = tz.split('/')[0] if '/' in timezone else 'Other'
            if region not in grouped:
                grouped[region] = []
            grouped[region].append(tz)

        return Response({
            'count': len(pytz.common_timezones),
            'grouped': grouped,
            'flat': pytz.common_timezones,
        })
