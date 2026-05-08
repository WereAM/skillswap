from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import UserProfile

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    '''
    Hooks into allauth's social login flow
    to create a UserProfile automatically
    '''

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        UserProfile.objects.get_or_create(user=user)
        return user