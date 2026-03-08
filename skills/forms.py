from django import forms
from .models import Skill, SkillCategory, UserSkill

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'description', 'difficulty_level', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class UserSkillForm(forms.ModelForm):
    class Meta:
        model = UserSkill
        fields = ['skill_type', 'proficiency_level',
                  'years_of_experience', 'availability_description']
        widgets = {
            'skill_type': forms.Select(attrs={'class': 'form-select'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-select'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'availability_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }

class SkillSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget = forms.TextInput(attrs={'placeholder': 'Search skills...'})
    )
    category = forms.ModelChoiceField(
        queryset = SkillCategory.objects.all(),
        required=False,
        empty_label='All Categories'
    )
    skill_type = forms.ChoiceField(
        choices=[
            ('', 'All Types'),
            ('offer', 'Offering'),
            ('request', 'Requesting'),
        ],
        required=False
    )
    proficiency_level = forms.ChoiceField(
        choices=[
            ('', 'All Levels'),
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        required=False
    )