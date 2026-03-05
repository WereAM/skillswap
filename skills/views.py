from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from skills.forms import SkillForm, SkillSearchForm, UserSkillForm
from skills.models import Skill, UserSkill


# Create your views here.
def skill_list(request):
    form = SkillSearchForm(request.GET)
    user_skills = UserSkill.objects.select_related(
        'user', 'skill', 'skill__category'
    )
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        skill_type = form.cleaned_data.get('skill_type')
        proficiency = form.cleaned_data.get('proficiency_level')

        if query:
            user_skills = user_skills.filter(
                Q(skill__name__icontains=query) | 
                Q(skill__description__icontains=query) | 
                Q(skill__username__icontains=query) 
            )
        if category:
            user_skills = user_skills.filter(skill__category=category)
        if skill_type:
            user_skills = user_skills.filter(skill_type=skill_type)
        if proficiency:
            user_skills = user_skills.filter(proficiency_level=proficiency)

    return render(request, 'skills/skills_list.html', {
        'user_skills': user_skills,
        'form': form,
    })

@login_required
def add_user_skill(request):
    if request.method == 'POST':
        skill_form = SkillForm(request.POST)
        user_skill_form = UserSkillForm(request.POST)

        if skill_form.is_valid() and user_skill_form.is_valid():
            # Check if the skill already exists, and create it if it doesn't
            skill, created = Skill.objects.get_or_create(
                name=skill_form.cleaned_data['name'],
                defaults={
                    'description': skill_form.cleaned_data['description'],
                    'difficulty_level': skill_form.cleaned_data['difficulty_level'],
                    'category': skill_form.cleaned_data['category'],
                }
            )
            user_skill = user_skill_form.save(commit=False)
            user_skill.user = request.user
            user_skill.skill = skill
            user_skill.save()
            messages.success(request, 'Skill added successfully!')
            return redirect('skills:my_skills')
        else:
            skill_form = SkillForm()
            user_skill_form = UserSkillForm()

        return render(request, 'skills/add_skill.html', {
            'skill_form': skill_form,
            'user_skill_form': user_skill_form,
        })

@login_required
def my_skills(request):
    user_skills = UserSkill.objects.filter(
        user = request.user
    ).select_related('skill', 'skill_category')
    return render(request, 'skills/skill_detail.html', {
        'user_skills' : user_skills
    })

def skill_detail(request, pk):
    user_skill = get_object_or_404(
        UserSkill.objects.select_related('user', 'skill'),
        pk=pk
    )
    return render(request, 'skills/skill_detail.html', {
        'user_skill': user_skill
    })

@login_required
def edit_user_skill(request, pk):
    user_skill = get_object_or_404(UserSkill, pk=pk, user=request.user)

    if request.method == 'POST':
        form = UserSkillForm(request.POST, instance=user_skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill Updated!')
            return redirect('skills:my_skills')
        
@login_required
def delete_user_skill(request, pk):
    user_skill = get_object_or_404(UserSkill, pk=pk, user=request.user)
    if request.method == 'POST':
        user_skill.delete()
        messages.success(request, 'skills/delete_skill.html', {
            'user_skill': user_skill
    })