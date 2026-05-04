# URL/API Reference

All URLs are server-rendered Django views returning HTML responses. SkillSwap does not currently have a REST API. This document covers all available URL endpoints.

## URL Namespaces

| Namespace | Prefix | App |
|---|---|---|
| `accounts` | `/accounts/` and `/` | accounts |
| `skills` | `/skills/` | skills |
| `swaps` | `/swaps/` | swaps |
| `messaging` | `/messaging/` | messaging |
| `allauth` | `/auth/` | django-allauth |

## accounts URLs
 
| URL | Name | Method | Auth Needed | Description |
|---|---|---|---|---|
| `/` | `accounts:home` | GET | No | Home page with stats |
| `/accounts/register/` | `accounts:register` | GET, POST | No | User registration |
| `/accounts/login/` | `accounts:login` | GET, POST | No | User login |
| `/accounts/logout/` | `accounts:logout` | GET | Yes | User logout |
| `/accounts/profile/` | `accounts:profile` | GET | Yes | Own profile page |
| `/accounts/profile/edit/` | `accounts:edit_profile` | GET, POST | Yes | Edit profile |
| `/accounts/user/<username>/` | `accounts:public_profile` | GET | No | Public profile |
| `/accounts/verify/<uuid>/` | `accounts:verify_email` | GET | No | Email verification |
| `/accounts/resend-verification/` | `accounts:resend_verification` | GET, POST | No | Resend verification email |

### Template Usage
```django
{% url 'accounts:home' %}
{% url 'accounts:register' %}
{% url 'accounts:login' %}
{% url 'accounts:logout' %}
{% url 'accounts:profile' %}
{% url 'accounts:edit_profile' %}
{% url 'accounts:public_profile' username=user.username %}
{% url 'accounts:verify_email' token=token.token %}
{% url 'accounts:resend_verification' %}
```

## skills URLs
 
| URL | Name | Method | Auth Needed | Description |
|---|---|---|---|---|
| `/skills/` | `skills:list` | GET | No | Browse all skills with search/filter |
| `/skills/mine/` | `skills:my_skills` | GET | Yes | Current user's skills |
| `/skills/add/` | `skills:add` | GET, POST | Yes | Add a new skill |
| `/skills/<pk>/` | `skills:detail` | GET | No | Skill detail page |
| `/skills/<pk>/edit/` | `skills:edit` | GET, POST | Yes | Edit own skill |
| `/skills/<pk>/delete/` | `skills:delete` | GET, POST | Yes | Delete own skill |

### Query Parameters (skills:list)
| Parameter | Type | Description |
|---|---|---|
| `query` | string | Search by skill name, description or username |
| `category` | int | Filter by SkillCategory ID |
| `skill_type` | string | Filter by `offer` or `request` |
| `proficiency_level` | string | Filter by `beginner`, `intermediate`, `advanced`, `expert` |

### Template Usage
```django
{% url 'skills:list' %}
{% url 'skills:my_skills' %}
{% url 'skills:add' %}
{% url 'skills:detail' pk=user_skill.pk %}
{% url 'skills:edit' pk=user_skill.pk %}
{% url 'skills:delete' pk=user_skill.pk %}
```

## swaps URLs
 
| URL | Name | Method | Auth Needed | Description |
|---|---|---|---|---|
| `/swaps/create/<skill_id>/` | `swaps:create` | GET, POST | Yes | Send a swap request |
| `/swaps/inbox/` | `swaps:inbox` | GET | Yes | Received swap requests |
| `/swaps/sent/` | `swaps:sent` | GET | Yes | Sent swap requests |
| `/swaps/<pk>/` | `swaps:detail` | GET, POST | Yes | Swap detail and session scheduling |
| `/swaps/<pk>/accept/` | `swaps:accept` | POST | Yes | Accept a swap (receiver only) |
| `/swaps/<pk>/deny/` | `swaps:deny` | POST | Yes | Deny a swap (receiver only) |
| `/swaps/<pk>/cancel/` | `swaps:cancel` | POST | Yes | Cancel a swap (sender only) |
| `/swaps/session/<id>/complete/` | `swaps:complete_session` | POST | Yes | Mark session as completed |
| `/swaps/session/<id>/review/` | `swaps:leave_review` | GET, POST | Yes | Leave a review |

### Access Control
| Action | Who can perform |
|---|---|
| View swap detail | Sender or receiver only |
| Accept swap | Receiver only |
| Deny swap | Receiver only |
| Cancel swap | Sender only |
| Schedule session | Either participant |
| Complete session | Either participant |
| Leave review | Either participant (once each) |

### Template Usage
```django
{% url 'swaps:create' skill_id=user_skill.pk %}
{% url 'swaps:inbox' %}
{% url 'swaps:sent' %}
{% url 'swaps:detail' pk=swap.pk %}
{% url 'swaps:accept' pk=swap.pk %}
{% url 'swaps:deny' pk=swap.pk %}
{% url 'swaps:cancel' pk=swap.pk %}
{% url 'swaps:complete_session' session_id=session.pk %}
{% url 'swaps:leave_review' session_id=session.pk %}
```

## messaging URLs
 
| URL | Name | Method | Auth needed | Description |
|---|---|---|---|---|
| `/messaging/` | `messaging:inbox` | GET | Yes | Message inbox |
| `/messaging/<username>/` | `messaging:conversation` | GET, POST | Yes | Conversation thread |
| `/messaging/notifications/` | `messaging:notifications` | GET | Yes | All notifications |
| `/messaging/notifications/<pk>/read/` | `messaging:mark_read` | GET | Yes | Mark specific notification as read |
| `/messaging/notifications/read-all/` | `messaging:mark_all_read` | GET | Yes | Mark all as read |

### Template Usage
```django
{% url 'messaging:inbox' %}
{% url 'messaging:conversation' username=user.username %}
{% url 'messaging:notifications' %}
{% url 'messaging:mark_read' pk=notification.pk %}
{% url 'messaging:mark_all_read' %}
```

## allauth URLs (Social Auth)
 
These URLs are handled automatically by django-allauth.
 
| URL | Description |
|---|---|
| `/auth/google/login/` | Initiate Google OAuth flow |
| `/auth/google/login/callback/` | Google OAuth callback |
| `/auth/login/` | Allauth login (fallback) |
| `/auth/signup/` | Allauth signup (fallback) |
 
### Template Usage
```django
{% load socialaccount %}
{% provider_login_url 'google' %}
```

## Admin URLs
 
| URL | Description |
|---|---|
| `/admin/` | Django admin dashboard |
 
Access requires a superuser account created with `python manage.py createsuperuser`.

## Global Template Context
 
These variables are available in every template via the context processor in `accounts/context_processors.py`:
 
| Variable | Type | Description |
|---|---|---|
| `unread_messages_count` | int | Unread direct messages for current user |
| `unread_notifications_count` | int | Unread notifications for current user |
 
Both return `0` for unauthenticated users.