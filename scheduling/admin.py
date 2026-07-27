from django.contrib import admin
from .models import AvailabilitySlots, SchedulingPreference, APIClient

@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_active', 'request_count', 'last_used', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'owner__username']
    readonly_fields = ['api_key', 'request_count', 'last_used', 'created_at']

# Register your models here.
admin.site.register(AvailabilitySlots)
admin.site.register(SchedulingPreference)