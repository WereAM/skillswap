from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from scheduling.models import APIClient

class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication for external API clients using their key
    """

    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')

        if not api_key:
            return None
        
        try:
            client = APIClient.objects.select_related('owner').get(
                api_key = api_key,
                is_active = True
            )
        except APIClient.DoesNotExist:
            raise AuthenticationFailed('Invalid or inactive API key.')
        
        # update usage tracking
        client.request_count += 1
        client.last_used = timezone.now()
        client.save(update_fields=['request_count', 'last_used'])

        return (client.owner, client)
    
    def authenticate_header(self, request):
        return 'X-API-Key'