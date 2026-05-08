from django.contrib import admin
from .models import UserProfile, EmailVerificationToken

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(EmailVerificationToken)