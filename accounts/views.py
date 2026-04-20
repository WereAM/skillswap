from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, UserProfileForm
from .models import UserProfile, EmailVerificationToken
from skills.models import UserSkill
from swaps.models import Review
from .email_utils import send_verification_email

# Create your views here.
def home(request):
    return render(request, 'home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            UserProfile.objects.create(user=user)
            send_verification_email(user)

            messages.info(
                request,
                'Account created. Please check your email to verify your account.'
            )
            return redirect('accounts:login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})
    
def verify_email(request, token):
    try:
        verification = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('accounts:login')
    
    if verification.is_expired():
        verification.delete()
        messages.error(
            request,
            'Verification link has expired. Please register again.'
        )
        return redirect('accounts:register')
    
    # activate the account
    user = verification.user
    user.is_active = True
    user.save()

    verification.delete()

    messages.success(request, 'Email verified successfully! Proceed to log in.')
    return redirect('accounts:login')

def resend_verification(request):
    '''
    Request new verification email if
    token expired or didn't receive it
    '''
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            send_verification_email(user)
            messages.success(
                request,
                'Verification email resent. Please check your inbox.'
            )
        except User.DoesNotExist:
            messages.info(
                request,
                'If your email exists and is unverified, '
                'we sent a new verification link.'
            )
    return render(request, 'accounts/resend_verification.html')

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

