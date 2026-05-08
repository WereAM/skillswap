# Changelog

All notable changes to SkillSwap are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Two-factor authentication (2FA)
- AI-powered skill matching
- Mobile app (React Native)
- Group skill swaps
- Scheduling calendar integration

## [1.1.0] - 2026-04-24

### Added
- Email verification on registration
- Google OAuth social login via django-allauth
- Resend verification email functionality

### Changed
- Updated allauth settings to non-deprecated format
- Registration flow now requires email verification before login


## [1.0.0] - 2026-04-19

### Added
- Notifications system with type-based icons
- Unread notification count in navbar
- Mark single/all notifications as read
- Notifications triggered on swap, message and review events

## [0.9.0] - 2026-04-18

### Added
- Direct messaging between users
- Conversation thread view with chat bubble UI
- Message inbox with conversation previews
- Unread message count in navbar
- Auto-scroll to latest message
- Send message button on public profiles
- Context processor for global unread counts

## [0.8.0] - 2026-03-19

### Added
- Initial production deployment on Railway
- PostgreSQL database integration
- Gunicorn + Whitenoise production setup
- Custom domain configuration
- CSRF trusted origins for production

## [0.7.0] - 2026-03-16

### Added
- Custom UI design system
- Playfair Display + DM Sans typography
- Teal and amber colour palette
- Hero section on home page with live stats
- Skill card grid with staggered animations
- CSS variables for consistent theming
- Responsive mobile layout
- How It Works section on home page

## [0.6.0] - 2026-03-11

### Added
- Review system — both participants can review after completed sessions
- Automatic rating average calculation on UserProfile
- Public profile pages showing skills, reviews and ratings
- Session completion workflow
- Clickable usernames throughout the platform

## [0.5.0] - 2026-03-10

### Added
- Swap request system (send, accept, deny, cancel)
- Session scheduling after swap acceptance
- Swap inbox and sent requests views
- Swap detail page with full status lifecycle
- Security checks — only participants can view/action swaps
- Duplicate request prevention
- Self-swap prevention

## [0.4.0] — 2026-03-08

### Added
- Skills app — add, edit, delete user skills
- Skill categories with seeded data
- Browse skills page with search and filter
- Search by name, category, type and proficiency
- Case-insensitive skill name matching
- Population script for test data

## [0.3.0] — 2026-03-01

### Added
- User authentication — register, login, logout
- UserProfile model extending Django's built-in User
- Profile picture upload
- Edit profile page
- Auto-create UserProfile on registration
- Login redirect handling with next parameter

## [0.2.0] — 2026-03-01

### Added
- Database models for all apps
- Migrations for accounts, skills, swaps, messaging
- Django admin registration for all models
- SkillCategory, Skill, UserSkill models
- SwapRequest, Session, Review models
- Message, Notification models

## [0.1.0] — 2026-02-23

### Added
- Initial Django project setup
- Four app structure: accounts, skills, swaps, messaging
- Git repository with dev/main branch strategy
- Virtual environment configuration
- Base settings with environment variable support
- PostgreSQL and SQLite database configuration