# SkillSwap

SkillSwap is a community-driven web platform that enables peer-to-peer skill exchange without monetary transactions. Users list skills they can teach and skills they want to learn, connect with matching users, and arrange skill swap sessions.

## Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Roadmap](#roadmap)

## Features
- **Authentication** - Email/password registration with email verification, Google OAuth login.
- **Skill Management** - List, browse, search and filter skills by category, type and proficiency.
- **Swap Requests** - Send, accept, deny and cancel skill swap requests.
- **Session Scheduling** - Schedule sessions with date, duration and meeting link.
- **Reviews and Ratings** - Leave reviews after completed sessions, automated rating calculation.
- **Messaging** - Direct messaging between users, with unread messages count.
- **Notifications** - Real-time notifications for swap requests and messages.
- **Public Profiles** - View any user's skills, ratings and reviews.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.x (Python 3.13) |
| Database | PostgreSQL (production) | SQLite (development) |
| Auth | Django Auth + django-allauth (Google OAuth) |
| Frontend | Django Templates + Bootstrap 5 + Custom CSS |
| Static Files | Whitenoise |
| Web Server | Gunicorn |
| Deployment | Railway |
| Email | Gmail SMTP |

## Quick Start

### Pre-requisites
- Python 3.11+
- pip + optional virtualenv
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/WereAM/skillswap.git
cd skillswap

# 2. Create and activate virtual environment
python -m venv venvname
venvename\Scripts\activate     # Windows
source venvname/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with the right values

# 5. Run migrations
python manage.py migrate

# 6. Seed the database
python populate.py

# 7. Create superuser
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver

```

Visit `https://127.0.0.1:8000` to see the app.

## Project Structure

```
skillswap/
|—— manage.py
|—— populate.py
|—— requirements.txt
|—— Procfile
|—— runtime.txt
|—— .env
|—— .env.example
|
|——skillswap/
|   |—— settings.py
|   |—— urls.py
│   └── wsgi.py
|
|—— accounts/
|—— messaging/
|—— skills/
|—— swaps/
|
|——templates/
|   |—— accounts/
|   |—— messaging/
|   |—— skills/
|   |—— swaps/
|   |—— base.html
|   └── home.html
|   
|—— static/
|   |—— css
|       └── main.css
|
└── docs/

```

## Documentation

| Document | Description |
|---|---|
| [Architecture Overview](docs/architecture/overview.md) | System design and architecture |
| [Database Schema](docs/architecture/database.md) | Models and relationships |
| [API Reference](docs/architecture/api.md) | URL endpoints |
| [Local Setup](docs/setup/local.md) | Development environment setup |
| [Deployment Guide](docs/setup/deployment.md) | Production deployment |
| [Environment Variables](docs/setup/environment.md) | All environment variables |
| [Contributing Guide](CONTRIBUTING.md) | How to contribute |
| [Changelog](CHANGELOG.md) | Version history |
| [Roadmap](docs/roadmap/roadmap.md) | Planned features |

## Contributing

All valuable contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## License

MIT License - see [LICENSE](LICENSE) for details.