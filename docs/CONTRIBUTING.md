# Contributing to SkillSwap

Thank you for your interest in contributing to SkillSwap! This document outlines the process for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Branch Strategy](#branch-strategy)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Reporting Bugs](#reporting-bugs)

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/skillswap.git
cd skillswap
```
3. Follow the [Local Setup Guide](docs/setup/local.md) to get your environment running
4. Create a new branch for your feature or fix

## Branch Strategy

We use the following branch structure:

```
main          ← production-ready code, always deployable
dev           ← integration branch, all features merge here first
feature/xxx   ← individual feature branches
bugfix/xxx    ← bug fix branches
hotfix/xxx    ← urgent production fixes
```

### Rules
- **Never commit directly to `main` or `dev`**
- Always branch off `dev` for new features
- Branch names should be descriptive: `feature/add-skill-ratings`, `bugfix/fix-swap-redirect`

## Development Workflow

```bash
# 1. Make sure you're on dev and up to date
git checkout dev
git pull origin dev

# 2. Create your feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes with regular commits
git add .
git commit -m "feat: add skill rating feature"

# 4. Push your branch
git push origin feature/your-feature-name

# 5. Open a Pull Request to dev on GitHub
```

## Code Standards

### Python / Django
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Maximum line length: 88 characters
- Use descriptive variable names - no single letter variables except in loops
- Every function and class must have a docstring explaining what it does
- Use Django's `get_object_or_404` for all object lookups in views
- Always use `select_related()` on querysets with foreign keys
- Never put business logic in templates - keep it in views or models

### Comments
- Comment the **why**, not the **what**
- Every view function must have a comment explaining its purpose
- Every model must have comments on non-obvious fields

```python
# Good
# We use get_or_create here because the profile might not exist
# for users created before the UserProfile model was added
profile, created = UserProfile.objects.get_or_create(user=request.user)

# Bad
# Get or create profile
profile, created = UserProfile.objects.get_or_create(user=request.user)
```

### Templates
- Always use `{% load static %}` at the top of templates that use static files
- Always extend `base.html`
- Always define `{% block title_block %}` and `{% block content_block %}`
- Never use inline styles - add classes to `main.css` instead

### CSS
- Use CSS variables defined in `:root` for all colours
- Follow the existing naming convention in `main.css`
- Mobile-first responsive design

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
type: short description (max 72 chars)

Optional longer description explaining the why.
```

### Types
| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | CSS/formatting changes |
| `refactor` | Code restructuring without feature change |
| `test` | Adding or updating tests |
| `chore` | Dependency updates, config changes |

### Examples
```bash
feat: add email verification on registration
fix: correct swap status not updating on cancel
docs: add deployment guide to README
style: update skill card hover animation
test: add swap acceptance test cases
```

## Pull Requests

### Before Submitting
- [ ] All existing tests pass: `python manage.py test`
- [ ] You have written tests for new features
- [ ] Code follows the style guidelines above
- [ ] You have added/updated documentation where needed
- [ ] No debug print statements left in code
- [ ] No hardcoded credentials or secrets

### PR Template
When opening a PR, include:

```
## What does this PR do?
Brief description of the changes.

## Why?
Explain the motivation or link to the issue.

## How to test?
Steps to test the changes locally.

## Screenshots (if UI changes)
Before/after screenshots.

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No debug code left
```

### Review Process
1. Open PR against `dev` branch
2. At least one review required before merging
3. All comments must be resolved
4. Tests must pass
5. Squash commits before merging for clean history

## Reporting Bugs

Open a GitHub Issue with:
- **Title**: Clear one-line description
- **Steps to reproduce**: Numbered list of exact steps
- **Expected behaviour**: What should happen
- **Actual behaviour**: What actually happens
- **Screenshots**: If relevant
- **Environment**: OS, Python version, Django version

## Questions?

Open a GitHub Discussion or reach out to the maintainer directly.