# Database Schema

## Overview

SkillSwap uses a relational database (PostgreSQL in production, SQLite in development). The schema is managed entirely through Django migrations.

## Entity Relationship Diagram

```
User (Django built-in)
|
|—— UserProfile (1:1)
|       └── rating_average, bio, location, profile_picture
|
|—— EmailVerificationToken (1:1)
|       └── token (UUID), created_at, is_expired()
|
|—— UserSkill  (many)
|       |—— skill (FK → Skill)
|       |—— skill_type (offer/request)
|       |—— proficiency_level
|       └── years_of_experience
|
|—— SwapRequest sender (many)
|—— SwapRequest receiver (many)
|       |—— offered_skill (FK → UserSkill)
|       |—— requested_skill (FK → UserSkill)
|       |—— status (pending/accepted/rejected/cancelled)
|       └── Session (1:1)
|               └── Review (many)
|
|—— Message sender (many)
|—— Message receiver (many)
└── Notification (many)

Skill
└── category (FK → SkillCategory)

SkillCategory
└── name, description
```

## Model Reference

### accounts app

#### `UserProfile`
Extends Django's built-in `User` model with additional fields.

| Field | Type | Description |
|---|---|---|
| `user` | OneToOneField(User) | Links to Django User | 
| `bio` | TextField | Optional user biography |
| `location` | CharField(100) | Optional location string |
| `profile_picture` | ImageField | Optional profile image |
| `rating_average` | DecimalField(3,2) | Auto-calculated average rating |

**Notes:**
- Auto-created on registration and Google login via adapter
- `rating_average` updated by `update_rating()` in `swaps/views.py`
- `get_or_create` used throughout to handle edge cases

### `EmailVerificationToken`
Stores a unique token for email verification.

| Field | Type | Description |
|---|---|---|
| `user` | OneToOneField(User) | The user being verified | 
| `token` | UUIDField | Unique unguessable token |
| `created_at` | DateTimeField | Token creation timestamp |

**Methods:**
- `is_expired()` — returns True if token is older than 1 hour.

**Notes:**
- Token deleted after successful verification
- Old tokens deleted before new ones are created (resend flow)

### skills app

#### `SkillCategory`
Top-level grouping for skills.

| Field | Type | Description |
|---|---|---|
| `name` | CharField(100) | Category name e.g. Technology | 
| `description` | TextField | Optional description |

**Seeded categories:** Technology, Language, Music, Cooking, Fitness, Art & Design, Academic, Other

#### `Skill`
The generic skill catalogue. Shared across users.

| Field | Type | Description |
|---|---|---|
| `name` | CharField(100) | Skill name e.g. Python Programming | 
| `description` | TextField | Optional description |
| `category` | ForeignKey(SkillCategory) | SET_NULL on delete |
| `created_at` | DateTimeField | Auto-set on creation |

**Notes:**
- `save() `overridden to normalise name to title case
- `get_or_create` with `name__iexact` prevents duplicates
- Skills are shared — one Skill record for "Python" regardless of how many users list it

#### `UserSkill`
Bridge table connecting a User to a Skill with metadata.

| Field | Type | Description |
|---|---|---|
| `user` | ForeignKey(User) | The user |
| `skill` | ForeignKey(Skill) | The skill |
| `skill_type` | CharField | offer or request |
| `proficiency_level` | CharField | beginner/intermediate/advanced/expert |
| `years_of_experience` | PositiveIntegerField | Years of experience |
| `availability_description` | TextField | Free text availability |
| `created_at` | DateTimeField | Auto-set on creation |

**Constraints:**
- `unique_together = [('user', 'skill', 'skill_type')]` — prevents duplicate skill/type per user

### swaps app

#### `SwapRequest`
Represents a proposed skill exchange between two users.

| Field | Type | Description |
|---|---|---|
| `sender` | ForeignKey(User) | User who initiated the swap |
| `receiver` | ForeignKey(User) | User who received the request|
| `offered_skill` | ForeignKey(UserSkill) | Skill the sender is offering |
| `requested_skill` | ForeignKey(UserSkill) | Skill the sender wants |
| `status` | CharField | pending/accepted/rejected/cancelled |
| `message` | TextField | Optional intro message |
| `created_at` | DateTimeField | Auto-set on creation |
| `updated_at` | DateTimeField | Auto-updated on save |

**Status lifecycle:**
```
pending → accepted → (session scheduled) → (session completed) → (reviews left)
        → rejected
        → cancelled
```

**Business rules enforced in views:**
- Only receiver can accept or deny
- Only sender can cancel
- Cannot swap with yourself
- Cannot have duplicate pending requests for same skill

#### `Session`
A scheduled meeting arising from an accepted swap.

| Field | Type | Description |
|---|---|---|
| `swap_request` | OneToOneField(SwapRequest) | The parent swap |
| `scheduled_date` | DateTimeField | When the session is |
| `duration_minutes` | PositiveIntegerField | Session length |
| `meeting_link` | URLField | Optional video call link |
| `status` | CharField | scheduled/completed/cancelled |
| `notes` | TextField | Optional session notes |

#### `Review`
A review left by one participant about another after a completed session.

| Field | Type | Description |
|---|---|---|
| `session` | ForeignKey(Session) | The session being reviewed |
| `reviewer` | ForeignKey(User) | Who left the review | 
| `reviewee` | ForeignKey(User) | Who is being reviewed |
| `rating` | PositiveSmallIntegerField | 1-5 star rating |
| `comment` | TextField | Optional written review |
| `created_at` | DateTimeField | Auto-set on creation |

**Constraints:**
- `unique_together = [('session', 'reviewer')]` — one review per person per session

**Notes:**
- Both participants can leave a review
- Saving a review triggers u`pdate_rating()` to recalculate the reviewee's average

### messaging app

#### `Message`
A direct message between two users

| Field | Type | Description |
|---|---|---|
| `sender` | ForeignKey(User) | Who sent the message |
| `receiver` | ForeignKey(User) | Who received it |
| `content` | TextField | Message body |
| `sent_at` | DateTimeField | Auto-set on send |
| `is_read` | BooleanField | Read status, default False

**Notes:**
- Messages marked as read when the receiver opens the conversation
- Unread count exposed via context processor

#### `Notification`
System notification for a user about platform events.

| Field | Type | Description |
|---|---|---|
| `user` | ForeignKey(User) | Who receives the notification |
| `notification_type` | CharField | Type from TYPE_CHOICES |
| `content` | TextField | Human-readable notification text |
| `is_read` | BooleanField | Read status, default False |
| `created_at` | DateTimeField | Auto-set on creation |

**Notification types:**
- `swap_request` — new swap request received
- `swap_accepted` — your swap request was accepted
- `swap_rejected` — your swap request was rejected
- `session_scheduled` — session marked as completed
- `new_message` — new direct message received
- `new_review` — new review received

## Migrations
All schema are managed through Django migrations.

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations

# Rollback a migration
python manage.py migrate app_name 0001
```

**N/B:** Always use `makemigrations` to edit migrations.