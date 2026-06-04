from django import forms
from swaps.models import Session
from .models import AvailabilitySlots, SchedulingPreference, TIMEZONE_CHOICES

class EnhancedSessionForm(forms.ModelForm):
    '''
    Session form with timezone, location and meeting link fields.
    Replaces the SessionForm in swaps/forms.py
    '''
    class Meta:
        model = Session
        fields = [
            'scheduled_date', 'duration_minutes', 'timezone',
            'is_virtual', 'meeting_link', 'location_name',
            'location_latitude', 'location_longitude', 'notes'
        ]
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'duration_minutes': forms.Select(
                choices=[
                    (30, '30 minutes'),
                    (45, '45 minutes'),
                    (60, '1 hour'),
                    (90, '1.5 hours'),
                    (120, '2 hours'),
                    (180, '3 hours'),
                ],
                attrs={'min': 1}),
            'timezone': forms.Select(
                choices=TIMEZONE_CHOICES,
                attrs={'class': 'form-select'}),
            'is_virtual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting link if virtual'}),
            'location_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter/search for a location if in-person',
                'id': 'location_search'}),
            'location_latitude': forms.HiddenInput(),
            'location_longitude': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Additional notes (optional)'}),
        }

'''
Form for adding/editing availability slots in the scheduling preferences.'''
class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlots
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

'''
Form for managing scheduling preferences, including availability slots and timezone selection.
'''
class SchedulingPreferenceForm(forms.ModelForm):
    class Meta:
        model = SchedulingPreference
        fields = ['timezone', 'buffer_minutes', 'reminder_hours']
        widgets = {
            'timezone': forms.Select(
                choices=TIMEZONE_CHOICES,
                attrs={'class': 'form-select'}),
            'buffer_minutes': forms.Select(
                choices=[(0, 'No buffer'), (15, '15 minutes'), (30, '30 minutes'), (60, '1 hour')],
                attrs={'class': 'form-select'}),
            'reminder_hours': forms.Select(
                choices=[(0, 'No reminder'), (1, '1 hour before'), (2, '2 hours before'), (5, '5 hours before'), (6, '6 hours before'), (12, '12 hours before'), (24, '24 hours before'), (48, '48 hours before')],
                attrs={'class': 'form-select'}),
        }