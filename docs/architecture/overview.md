# Architecture Overview

## System Architecture

SkillSwap follows Django's MVT (Model-View-Template) architecture pattern across four independent Django apps, connected through a central project configuration.

## High Level Architecture

```
Browser
    ↓ HTTP Request
Gunicorn (WSGI Server)
    ↓ 
Django Application
    |—— URL Pouter (skillswap/urls.py)
    |       ↓
    |—— Views (business logic)
    |       ↓
    |—— Model (database layer)
    |       ↓
    └── Templates (HTML rendering)
            ↓
        HTTP Response   →   Browser

Static Files    →   Whitenoise  →   Browser
Media Files     →   Django Dev Server (local) / Cloud Storage (production)
Emails  →   Console Backend (local) / Gmail SMTP (production)

```

## App Structure

```
skillswap/          - Django project (router, settings)
|—— accounts/       - Authentication, profiles, public profiles
|—— messaging/      - Direct messages, notification
|—— skills/         - Skill catalogue and user skill management
└── swaps/          - Swap requests, sessions, reviews

```

### App Functionalities
**`accounts`**
- User registration with email verification
- Google OAuth via django-allauth
- Login, logout, password management
- UserProfile creation and editing
- Public profile pages
- Email verification tokens
- Context processor for global template data

**`skills`**
- Skill category management
- Generic skill catalogue (case-insensitive deduplication)
- UserSkill - user's relationship to a skill (offering/requesting)
- Search and filter functionality using Django Q objects
- Population script integration

**`swaps`**
- SwapRequest lifecycle (pending → accepted/rejected/cancelled)
- Session scheduling after swap acceptance
- Session completion workflow
- Review system with automatic rating recalculation
- Security enforcement - participant-only access

**`messaging`**
- Direct messaging between two users
- Conversation threading
- Unread message tracking
- Notification creation and management
- Notification utility (`utils.py`) used by other apps

## Request/Response Flow

### Typical Page Request
```
1. Browser sends GET /skills/
2. Django URL router matches → skills.views.skill_list
3. View queries UserSkill.objects.filter(...).select_relates(...)
4. View passes queryset to render()
5. Django template engine renders skill/skill_list.html
6. Response sent to browser
```

### Form Submission
```
1. Browser sends POST /skills/add/ with form data
2. CSRF middleware validates token
3. View instantiates SkillForm and UserSkillForm with POST data
4. Forms validate - If invalid, re-render with errors
5. If valid, save to database with commit=False pattern
6. Attach server-side data (user, skill)
7. Save to database
8. Redirect to success page (PRG pattern)
```

## Key Design Decisions

### 1. Centralised Templates

All templates live in a single root `templates/` directory with app subfolders. This allows shared layouts without complex app configuration.

### 2. UserSkill as Bridge Table

Rather than dtoring skill type on the Skill model, a `UserSkill` table connects users to skills with additional metadata (skill_type, proficiency_level, availability). This allows the same skill to be offered by one user and requested by another.

### 3. SwapRequest links to UserSkill not Skill

Swap requests reference `UserSkill` instances, not generic `Skill` objects. This captures the specific user's proficiency and availability context at the time of the request.

### 4. Notification Utility Pattern

The `messaging/utils.py` helper allows any app to create notification without importing views. This prevents circular imports between apps.

### 5. Context Processor for Global Data

Unread message and notification counts are injected into every template via a context processor in `accounts/context_processors.py`, avoiding the need to pass these values from every view manually.

### 6. Email Backend Switching

The email backend switches automatically between console (development) and SMTP (production) based on the `DEBUG` setting, allowing local development without a real email server.

## Security Architecture

| Concern | Implementation |
|---|---|
| Authentication | Django's built-in auth + allauth |
| Authorisation | `@login_required` decorator + manual participant checks |
| CSRF | Django's built-in CSRF middleware |
| Password hashing | Django's PBKDF2 with SHA256 |
| Secret key | Environment variable |
| Email verification | UUID token with 1-hour expiry |
| Object-level permissions | `get_object_or_404` with ownership filter |
| XSS | Django's template auto-escaping |
| SQL injection | Django ORM parameterised queries |

## Performance Considerations

| Technique | Where Used |
|---|---|
| `select_related()` | All views with ForeignKey traversal |
| `get_or_create()` | Skill deduplication, UserProfile creation |
| Static file compression | Whitenoise CompressedStaticFileStorage |
| Database connection pooling | `conn_max_age=600` in DATABASE config |
| Query count minimisation | Related data fetched in single JOIN queries |

## External Dependencies

| Package | Purpose | Version |
|---|---|---|
| Django | Web framework | 6.x |
| gunicorn | WSGI production server | 25.x |
| whitenoise | Static file serving | 6.x |
| django-allauth | Social authentication | Latest |
| dj-database-url | Database URL parsing | 3.x |
| psycopg2-binary | PostgreSQL adapter | 2.9.x |
| Pillow | Image processing | 12.x |
| python-dotenv | Environment variable loading | 1.x |