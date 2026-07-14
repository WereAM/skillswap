from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..utils.suggestions import get_smart_suggestions
from ..utils.conflicts import check_conflict

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggest_times(request):
    '''
    GET /api/scheduling/suggest/?swap+pk=1&duration=60
    Returns smart time suggestions for two users
    '''
    ...

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_conflict_api(request):
    '''
    POST /api/scheduling/conflicts/
    Body: {datetime, duration, timezone}
    Returns conflict status
    '''
    ...