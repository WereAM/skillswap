from django.contrib import admin
from .models import AvailabilitySlots, SchedulingPreference

# Register your models here.
admin.site.register(AvailabilitySlots)
admin.site.register(SchedulingPreference)