from django import forms

from skills.models import UserSkill
from .models import Session, SwapRequests, Review

class SwapRequestForm(forms.ModelForm):
    class Meta:
        model = SwapRequests
        # the user only sets the message and skill
        fields = ['offered_skill', 'message']
        widgets = {
            'message' : forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': "Introduce yourself and explain why you want to swap."
            }),
            'offered_skill': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # only show the current user's OFFERED skills
        self.fields['offered_skill'].queryset = UserSkill.objects.filter(
            user = user,
            skill_type = 'offer'
        ). select_related('skill')
        self.fields['offered_skill'].label = 'Skill you are offering'

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['scheduled_date', 'duration_minutes', 'meeting_link', 'notes']
        widgets = {
            'scheduled_date' : forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class' : 'form-control'
                }
            ),
            'duration_minutes' : forms.NumberInput(attrs={'class': 'form-control'}),
            'meeting_link' : forms.URLInput(attrs={'class': 'form-control'}),
            'notes' : forms.Textarea(attrs={
                'rows' : 3,
                'class' : 'form-control'
            }),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} ⭐') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Share your rating of this swap...'
            }),
        }