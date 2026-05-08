# Deployment Guide

This guide covers deploying SkillSwap to Railway with PostgreSQL.

## Prerequisites

- Railway account ([railway.app](https://railway.app))
- GitHub repository with your code
- Gmail account for email sending
- Google Cloud Console project for OAuth (optional)

## Required Files

Make sure these files exist in your project root:

**`Procfile`** — tells Railway how to start the app:
```
web: gunicorn skillswap.wsgi --log-file -
```

**`railway.json`** — Railway configuration:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "gunicorn skillswap.wsgi --log-file -",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**`runtime.txt`** — Python version:
```
python-3.13.0
```

**`requirements.txt`** — must include:
```
Django
gunicorn
whitenoise
dj-database-url
psycopg2-binary
python-dotenv
Pillow
django-allauth
```

## Step 1: Prepare Settings

Make sure `settings.py` has:

```python
# Whitenoise for static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← second position
    ...
]

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# CSRF - add your Railway domain
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://your-custom-domain.com',
]

# Allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.railway.app']
```

## Step 2: Deploy on Railway

### Option A — GitHub (Recommended)
1. Go to [railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Railway auto-detects Python and starts building

### Option B — Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inside your project folder
railway init
railway up
```

## Step 3: Add PostgreSQL

1. In your Railway project dashboard click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway creates the database and links it to your project
4. `DATABASE_URL` is automatically added to your app's environment

## Step 4: Set Environment Variables

In Railway dashboard → your app service → **Variables** tab, add:

```
SECRET_KEY=<generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-gmail@gmail.com
FRONTEND_URL=https://your-app.railway.app
```

> **Note:** `DATABASE_URL` is added automatically by Railway when you add PostgreSQL.

## Step 5: Run Migrations

After deployment, run migrations against the production database:

```bash
# Using Railway CLI
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python populate.py
```

Or via Railway dashboard shell if available.

## Step 6: Configure Google OAuth for Production

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Your existing OAuth app → **Credentials** → edit your OAuth Client
3. Add production redirect URI:
```
https://your-app.railway.app/auth/google/login/callback/
```
4. In your production Django admin (`/admin/`):
   - Update **Sites** domain to your Railway domain
   - Update **Social Applications** → Google → move new site to chosen

## Step 7: Verify Deployment

Visit your Railway URL and check:
- [ ] Home page loads with CSS
- [ ] Registration works and sends verification email
- [ ] Login works
- [ ] Google login works
- [ ] Skills browse page loads
- [ ] Admin panel accessible at `/admin/`

## Ongoing Deployments

Railway automatically redeploys when you push to your connected branch:

```bash
git add .
git commit -m "feat: your change"
git push origin main
```

Watch the build in Railway dashboard → **Deployments**.

After deploying code changes that include model changes:
```bash
railway run python manage.py migrate
```

## Troubleshooting

### Static files not loading
```bash
railway run python manage.py collectstatic --noinput --clear
```

### 500 Server Error
Enable debug temporarily in Railway Variables:
```
DEBUG=True
```
Visit the page to see the full error, then set back to `False`.

### CSRF Verification Failed
Add your domain to `CSRF_TRUSTED_ORIGINS` in `settings.py`.

### Gunicorn not found
Make sure `gunicorn` is in `requirements.txt` and run:
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: update requirements"
git push origin main
```

### Database connection errors
- Check `DATABASE_URL` is set in Railway Variables
- Use the internal URL (not public URL) for the running app
- Use the public URL only for `railway run` commands from local machine