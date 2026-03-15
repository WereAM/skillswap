from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, UserProfileForm
from .models import UserProfile
from skills.models import UserSkill
from swaps.models import Review

# Create your views here.
def home(request):
    return render(request, 'home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:profile')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or ('accounts:profile')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user = request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user = request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated')
            return redirect('accounts:profile')
        return render(request, 'accounts/edit_profile.html', {'form': form})
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form':form})
    
@login_required
def public_profile(request, username):
    # get the user
    viewed_user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user = viewed_user)

    # get the user's skills
    offered_skills = UserSkill.objects.filter(
        user = viewed_user,
        skill_type = 'offer'
    ).select_related('skill')

    requested_skills = UserSkill.objects.filter(
        user = viewed_user,
        skill_type = 'request'
    ).select_related('skill')

    # get their reviews
    reviews = Review.objects.filter(
        reviewee = viewed_user
    ).select_related('reviewer').order_by('-created_at')

    return render(request, 'accounts/public_profile.html', {
        'viewed_user' : viewed_user,
        'profile' : profile,
        'offered_skills' : offered_skills,
        'requested_skills' : requested_skills,
        'reviews' : reviews,
    })

