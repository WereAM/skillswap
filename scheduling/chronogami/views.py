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
    
# SCEDULING ENDPOINTS

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggest_times(request):
    '''
    GET /chronogami/scheduling/suggest/?swap+pk=1&duration=60
    Returns smart time suggestions for two users
    '''
    ...

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_conflict_api(request):
    '''
    POST /chronogami/scheduling/conflicts/
    Body: {datetime, duration, timezone}
    Returns conflict status
    '''
    ...