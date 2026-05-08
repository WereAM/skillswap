# Authentication

## Overview

SkillSwap uses a multi-layered authentication system built on Django's built-in `auth` module, extended with email verification and Google OAuth via `django-allauth`. The goal is to ensure every user on the platform is a real, verifiable person, which is essential for a trust-based community.

## How it Works

### Email/Password Registration Flow

```
User fills registration form
    → Account created with is_active=False
        → UserProfile auto-created
            → Verification email sent
                → User clicks link in email
                    → Account activated (is_active=True)
                        → Redirected to login
```

The key design decision here is setting `is_active=False` on registration. This means the user cannot log in at all until they verify their email, preventing fake or mistyped email addresses from accumulating on the platform.

### Google OAuth Flow

```
User clicks "Continue with Google"
    → Redirected to Google consent screen
        → User approves
            → Google redirects back with auth code
                → allauth exchanges code for user info
                    → Account created or matched to existing
                        → UserProfile auto-created via adapter
                            → User logged in
                                → Redirected to profile
```

Google login bypasses email verification since Google accounts are already verified by Google.

### Login Flow

```
User submits username/password
    → Django authenticates credentials
        → If valid and is_active=True → logged in
        → If valid but is_active=False → error (unverified)
        → If invalid → error message
            → Redirected to next URL or profile
```

## Technical Implementation

### Models

**`UserProfile`** (`accounts/models.py`)
Extends Django's built-in `User` via `OneToOneField`. Stores bio, location, profile picture and rating average.

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
```

**`EmailVerificationToken`** (`accounts/models.py`)
Stores a UUID token per user for email verification. Expires after 24 hours.

```python
class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=24)
```

### Views (`accounts/views.py`)

| View | Purpose |
|---|---|
| `register` | Creates inactive user, sends verification email |
| `user_login` | Authenticates and logs in user |
| `user_logout` | Logs out user |
| `verify_email` | Activates account on token click |
| `resend_verification` | Sends fresh verification email |
| `profile` | Shows own profile |
| `edit_profile` | Updates UserProfile fields |
| `public_profile` | Shows any user's public profile |

### Forms (`accounts/forms.py`)

| Form | Purpose |
|---|---|
| `RegisterForm` | Extends UserCreationForm with email, first/last name |
| `UserProfileForm` | Bio, location, profile picture fields |

### Email Utility (`accounts/email_utils.py`)

`send_verification_email(user)` — creates a fresh token, deletes any existing one, builds the verification URL and sends the email.

### Social Account Adapter (`accounts/adapters.py`)

`SocialAccountAdapter` extends allauth's default adapter to auto-create a `UserProfile` when a user signs up via Google for the first time.

### Context Processor (`accounts/context_processors.py`)

Makes `unread_messages_count` and `unread_notifications_count` available in every template automatically, without passing them from each view manually.

## URLs

| URL | View | Description |
|---|---|---|
| `/accounts/register/` | `register` | Registration page |
| `/accounts/login/` | `user_login` | Login page |
| `/accounts/logout/` | `user_logout` | Logout |
| `/accounts/profile/` | `profile` | Own profile |
| `/accounts/profile/edit/` | `edit_profile` | Edit profile |
| `/accounts/user/<username>/` | `public_profile` | Public profile |
| `/accounts/verify/<uuid>/` | `verify_email` | Email verification |
| `/accounts/resend-verification/` | `resend_verification` | Resend email |
| `/auth/google/login/` | allauth | Google OAuth |

## Email Configuration

| Environment | Backend | Behaviour |
|---|---|---|
| Development (`DEBUG=True`) | Console | Emails printed to terminal |
| Production (`DEBUG=False`) | SMTP | Real emails via Gmail |

Email credentials are stored in environment variables — never in code. See [environment.md](../setup/environment.md) for setup.

## Google OAuth Setup

### Local Development
1. Create project in [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth Client ID (Web Application)
3. Add redirect URI: `http://127.0.0.1:8000/auth/google/login/callback/`
4. In Django admin:
   - Update **Sites** domain to `127.0.0.1:8000`
   - Add **Social Application** with Client ID and Secret

### Production
1. Add production redirect URI to Google Cloud Console:
   `https://your-domain.railway.app/auth/google/login/callback/`
2. In production Django admin:
   - Update **Sites** domain to your production domain
   - Update **Social Application** with same credentials

### allauth Settings
```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```

## Key Design Decisions

### Why `is_active=False` until verified?
Without this, anyone can register with a fake email and immediately use the platform. Since SkillSwap connects real people for real skill exchanges, unverified accounts undermine trust. Setting `is_active=False` gates login behind email ownership proof.

### Why UUID tokens over time-based tokens?
UUID tokens are simple, stateless and database-backed. Django's `PasswordResetToken` uses HMAC-based tokens which are harder to understand and debug. For a student/early-stage project, UUID tokens stored in the database are more transparent and easier to manage.

### Why allauth for Google login?
Building OAuth from scratch requires handling token exchange, refresh tokens, error states and security edge cases. allauth has handled all of these for years across thousands of projects. No reason to rebuild it.

### Why store Google credentials in Django admin not .env?
allauth's design uses the database for social app credentials so they can be updated without redeployment. Multiple social providers can be managed through the same admin interface.

## Known Limitations

- No password reset flow yet (forgot password)
- Profile picture not resized on upload - large images stored at full size
- No account deletion feature
- Google login doesn't enforce email verification since Google handles it

## Future Improvements

- [ ] Forgot password / password reset flow
- [ ] Two-factor authentication (TOTP via Google Authenticator)
- [ ] Profile picture auto-resize to 300x300 on upload
- [ ] Account deletion with data cleanup
- [ ] GitHub OAuth (useful for tech-focused users)
- [ ] University email domain restriction (e.g. only @glasgow.ac.uk)
- [ ] Session management (view and revoke active sessions)