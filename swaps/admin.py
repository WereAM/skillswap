from django.contrib import admin
from .models import Session, SwapRequests, Review

# Register your models here.
admin.site.register(Session)
admin.site.register(SwapRequests)
admin.site.register(Review)