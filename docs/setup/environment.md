# Environment Variables Reference

All environment variables are loaded from a `.env` file in the project root using `python-dotenv`.

## .env.example

Copy this to `.env` and fill in your values:

```bash
# ==============================================
# SKILLSWAP ENVIRONMENT VARIABLES
# ==============================================
# Copy this file to .env and fill in your values
# Don't commit .env to Git
# ==============================================

# ---- Django Core ----
SECRET_KEY=your-secret-key-here
DEBUG=True

# ---- Database ----
# Leave empty for local SQLite
# Set to PostgreSQL URL for production
# DATABASE_URL=postgresql://user:password@host:5432/dbname

# ---- Email ----
# Local dev uses console backend (prints to terminal)
# Production requires real SMTP credentials
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# ---- URLs ----
# Used for building email verification links
FRONTEND_URL=http://127.0.0.1:8000
```

## Variable Reference

### Django Core

#### `SECRET_KEY`
**Required:** Yes

**Description:** Django's secret key used for cryptographic signing of cookies, sessions and tokens. Must be long, random and unique per environment.

**Generate a new key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Local:** Any string works, e.g. `local-dev-key-not-secure`

**Production:** Use the generated key above. Never use `django-insecure-` prefix keys in production.

#### `DEBUG`
**Required:** Yes

**Values:** `True` or `False`

**Description:** Controls Django's debug mode.

| Setting | Development | Production |
|---|---|---|
| `DEBUG=True` | Shows detailed error pages | **Never use** |
| `DEBUG=False` | Shows generic 500 page | Required |

**Effects of DEBUG=True:**
- Detailed error pages with tracebacks
- Console email backend (emails print to terminal)
- Static files served by Django dev server
- No security headers enforced

### Database

#### `DATABASE_URL`
**Required:** No (defaults to SQLite)

**Format:** `postgresql://user:password@host:port/dbname`

**Description:** Database connection URL. When not set, SQLite is used automatically.

**Local development:** Leave unset. SQLite is used automatically

**Production:** Set to your PostgreSQL connection URL

**Railway internal URL (use when app runs on Railway):**
```
postgresql://postgres:password@postgres.railway.internal:5432/railway
```

**Railway public URL (use when running railway run commands locally):**
```
postgresql://postgres:password@roundhouse.proxy.rlwy.net:PORT/railway
```

### Email

#### `EMAIL_HOST`
**Required:** Production only

**Default:** `smtp.gmail.com`

**Description:** SMTP server hostname for sending emails.

#### `EMAIL_PORT`
**Required:** Production only

**Default:** `587`

**Description:** SMTP server port. Use 587 for TLS, 465 for SSL.

#### `EMAIL_HOST_USER`
**Required:** Production only

**Description:** Gmail address used to send emails from.

#### `EMAIL_HOST_PASSWORD`
**Required:** Production only

**Description:** Gmail App Password (not your regular Gmail password).

**How to get a Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate a password for "Mail"
5. Use the 16-character code as `EMAIL_HOST_PASSWORD`

#### `DEFAULT_FROM_EMAIL`
**Required:** Production only

**Description:** The "From" address on outgoing emails. Usually same as `EMAIL_HOST_USER`.

### URLs

#### `FRONTEND_URL`
**Required:** Yes

**Description:** Base URL of the application. Used to build email verification links.

| Environment | Value |
|---|---|
| Local development | `http://127.0.0.1:8000` |
| Production | `https://your-app.railway.app` |

### Google OAuth (Optional)

Google OAuth credentials are stored in the Django database via the admin panel, not in environment variables. See [authentication.md](../features/authentication.md) for setup instructions.

---

## Railway Environment Variables

When deploying to Railway, set these in your service's Variables tab:

```
SECRET_KEY=<generated-secret-key>
DEBUG=False
DATABASE_URL=<railway-internal-postgresql-url>
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-gmail@gmail.com
FRONTEND_URL=https://your-app.railway.app
```

## Security Notes

- Never commit `.env` to Git. It's in `.gitignore`
- Never use `DEBUG=True` in production
- Never use `django-insecure-` prefix keys in production
- Rotate your `SECRET_KEY` if it's ever exposed
- Use Gmail App Passwords, not your real Gmail password
- Store production credentials only in your hosting platform's environment variable manager