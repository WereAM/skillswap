# Local Development Setup

This guide walks you through setting up SkillSwap on your local machine for development.

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.13+ | [python.org](https://python.org) |
| Git | Latest | [git-scm.com](https://git-scm.com) |
| pip | Latest | Comes with Python |

## Step 1 — Clone the Repository

```bash
git clone https://github.com/WereAM/skillswap.git
cd skillswap
```

## Step 2 — Create Virtual Environment

```bash
# Create the environment
python -m venv 'venvname'

# Activate it
'venvname'\Scripts\activate     # Windows
source 'venvname'/bin/activate  # Mac/Linux
```

You should see your `('venvname')` at the start of your terminal prompt.

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4 — Environment Variables

Create a `.env` file in the project root:

```bash
# Minimum required for local development
SECRET_KEY=any-long-random-string-here
DEBUG=True
FRONTEND_URL=http://127.0.0.1:8000
```

See [environment.md](environment.md) for all available variables.

> **Note:** `.env` is in `.gitignore` to avoid committing to Git.

## Step 5 — Database Setup

```bash
# Apply all migrations
python manage.py migrate

# Seed categories, skills and test users
python populate.py
```

The population script creates:
- 8 skill categories
- 12 sample skills
- 2 test users (`testuser` and `testuser2`, password: `password123`)

## Step 6 — Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts. This gives you access to `/admin/`.

## Step 7 — Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## Useful Development URLs

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Home page |
| `http://127.0.0.1:8000/admin/` | Admin dashboard |
| `http://127.0.0.1:8000/skills/` | Browse skills |
| `http://127.0.0.1:8000/accounts/register/` | Registration |

## Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test accounts
python manage.py test skills
python manage.py test swaps

# Run with verbosity
python manage.py test --verbosity=2
```

## Development Email

In development, emails are printed to the terminal instead of being sent. When you register a new account, look for the verification URL in your terminal output:

```
Content-Type: text/plain; charset="utf-8"
Subject: Verify your SkillSwap account

Hi testuser,

http://127.0.0.1:8000/accounts/verify/550e8400-e29b-41d4-a716-446655440000/
```

Copy and paste the URL into your browser to verify the account.

## Google Social Login (Local)

To test Google login locally:

1. Set up credentials in [Google Cloud Console](https://console.cloud.google.com)
2. Add `http://127.0.0.1:8000/auth/google/login/callback/` as an authorised redirect URI
3. Add credentials via Django admin:
   - Go to `/admin/sites/site/` → update domain to `127.0.0.1:8000`
   - Go to `/admin/socialaccount/socialapp/add/` → add Google credentials

See [authentication.md](../features/authentication.md) for detailed instructions.

## Resetting the Database

If you need a fresh start:

```bash
# Delete the SQLite database
del db.sqlite3          # Windows
rm db.sqlite3           # Mac/Linux

# Re-run migrations
python manage.py migrate

# Re-seed data
python populate.py

# Re-create superuser
python manage.py createsuperuser
```

## Common Issues

**`python` not recognised**
Make sure your virtual environment is activated. You should see your `(venvname)` in your prompt.

**`ModuleNotFoundError`**
Run `pip install -r requirements.txt` with your virtual environment activated.

**`No such table` errors**
Run `python manage.py migrate` to apply all migrations.

**Static files not loading**
Run `python manage.py collectstatic` and make sure `STATICFILES_DIRS` points to your `static/` folder in `settings.py`.

**Port already in use**
```bash
python manage.py runserver 8001
```
Then visit `http://127.0.0.1:8001`.