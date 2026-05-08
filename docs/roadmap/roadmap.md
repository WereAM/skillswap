# Product Roadmap

## Current Version: 1.1.0

## Vision

SkillSwap aims to become the go-to platform for peer skill exchange, starting with university communities and expanding to cities, then globally. The long-term vision is a world where anyone can access any skill without financial barriers.

## Completed

### Core Platform (v1.0.0)
- User registration and authentication
- Email verification
- Google OAuth social login
- User profiles with ratings
- Skill management (add, edit, delete, search, filter)
- Swap request system (send, accept, deny, cancel)
- Session scheduling
- Review and rating system
- Direct messaging
- Notifications
- Custom UI design system
- Production deployment on Railway
- PostgreSQL database
- Automated test suite

## Near Term (v1.2.0) - Next 30 Days

### Security & Trust
- [ ] Two-factor authentication (2FA) — optional for users
- [ ] Profile verification badge for verified email users
- [ ] Report/flag inappropriate content
- [ ] Block user functionality

### UX Improvements
- [ ] Pagination on skills browse page
- [ ] Loading states on form submissions
- [ ] Better mobile navigation
- [ ] Image optimisation on upload (auto-resize profile pictures)
- [ ] Skill endorsements from swap partners

### Platform
- [ ] Custom domain setup
- [ ] Basic analytics dashboard for admin
- [ ] Sitemap.xml for SEO
- [ ] robots.txt

## Medium Term (v1.3.0 - v1.5.0) - 1-3 Months

### AI Features
- [ ] AI-powered skill matching suggestions
- [ ] Smart swap recommendations based on profile
- [ ] Automated skill description suggestions

### Discovery
- [ ] Featured skills on home page
- [ ] Category browse pages
- [ ] User directory
- [ ] Location-based filtering

### Scheduling
- [ ] Integrated calendar for availability
- [ ] Automated session reminders via email
- [ ] Calendar export (iCal/Google Calendar)
- [ ] Rescheduling requests

### Community
- [ ] Skill groups/communities
- [ ] Community forums per skill category
- [ ] Leaderboard for most active swappers
- [ ] Achievement badges
- [ ] Animated progress charts

## Long Term (v2.0.0+) - 3-12 Months

### Monetisation
- [ ] Premium verified profiles
- [ ] Featured skill listings
- [ ] SkillSwap Pro subscription (advanced analytics, priority support)
- [ ] White-label platform for universities and companies

### Platform Expansion
- [ ] Mobile app (React Native)
- [ ] Browser extension for quick skill lookup
- [ ] API for third-party integrations
- [ ] Zapier integration

### Trust & Safety
- [ ] Identity verification (ID check)
- [ ] Background checks for sensitive skill categories
- [ ] Dispute resolution system
- [ ] Insurance partnership for in-person sessions

### Enterprise
- [ ] University partnership programme
- [ ] Corporate SkillSwap for internal skill sharing
- [ ] Analytics dashboard for organisations
- [ ] SSO (Single Sign-On) for enterprise clients

## Architectural Decisions Log

### ADR-001: SQLite → PostgreSQL
**Date:** March 2026

**Decision:** Switched from SQLite to PostgreSQL for production

**Reason:** SQLite resets on Railway container restart, losing all data

**Status:** Implemented

### ADR-002: Custom CSS over Bootstrap theme
**Date:** March 2026

**Decision:** Layer custom CSS on Bootstrap rather than use a pre-built theme

**Reason:** Unique brand identity more important than speed for a product launch

**Status:** Implemented

### ADR-003: django-allauth for social auth
**Date:** March 2026

**Decision:** Use django-allauth instead of building OAuth from scratch

**Reason:** Battle-tested library handling edge cases we'd miss building our own

**Status:** Implemented

### ADR-004: UserSkill as bridge table
**Date:** February 2026

**Decision:** Separate UserSkill from Skill model

**Reason:** Same skill can be offered by one user and requested by another — needs its own metadata

**Status:** Implemented

### ADR-005: Notification utility pattern
**Date:** March 2026

**Decision:** Create notifications via utility function rather than signals

**Reason:** Simpler to understand for a small team, avoids Django signals complexity

**Tradeoff:** Less decoupled than signals — revisit when team grows

**Status:** Implemented

## How to Contribute to the Roadmap

Have a feature idea? Open a GitHub Issue with the label `enhancement` and describe:
1. The problem it solves
2. Who benefits from it
3. A rough description of how it might work

The maintainer reviews all suggestions and adds promising ones to the roadmap.