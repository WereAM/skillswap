from accounts.models import EmailVerificationToken
from django.conf import settings
from django.core.mail import send_mail


def send_verification_email(user):
    '''
    Creates a verification token and sends the email 
    to the user, after registration
    '''

    # delete any existing token for specific user
    EmailVerificationToken.objects.filter(user=user).delete()

    # create new token
    token = EmailVerificationToken.objects.create(user=user)

    verification_url = (
        f'{settings.FRONTEND_URL}/accounts/verify/{token.token}/'
    )

    send_mail(
        subject='Verify your SkillSwap account',
        message=f'''
        Hello there {user.first_name or user.username},

        Welcome to SkillSwap! Please verify your email address by clicking the link below:

        {verification_url}

        This link expires in 1 hour.

        If you did not create an account, please ignore this email.

        The SkillSwap Team
            ''',
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [user.email],
            fail_silently = False,
    )