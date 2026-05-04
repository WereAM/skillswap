# Skills

## Overview

The skills system is the core of SkillSwap's marketplace. It has two layers: a shared skill catalogue (`Skill`) and a user-specific skill listing (`UserSkill`). This separation means "Python Programming" exists once in the database but can be offered by many users and requested by many others, each with their own proficiency level and availability.

## How it Works

### Adding a Skill

```
User clicks "Add Skill"
    → Fills in skill details (name, category)
    → Fills in their experience (type, proficiency, availability)
        → View checks if skill name already exists (case-insensitive)
            → Creates Skill if new, reuses existing if found
                → Creates UserSkill linking user to skill
                    → Redirected to My Skills page
```

### Browsing Skills

```
User visits /skills/
    → All UserSkill objects fetched with related data
        → Optional: filter by query, category, type, proficiency
            → Results rendered as card grid
                → Each card links to skill detail page
```

### Search and Filter

The search uses Django's `Q` objects to perform OR queries across multiple fields simultaneously:

```python
user_skills = user_skills.filter(
    Q(skill__name__icontains=query) |
    Q(skill__description__icontains=query) |
    Q(user__username__icontains=query) |
    Q(user__first_name__icontains=query) |
    Q(user__last_name__icontains=query)
)
```

Filters are chained so each applied filter narrows the results further (AND logic):

```python
if category:
    user_skills = user_skills.filter(skill__category=category)
if skill_type:
    user_skills = user_skills.filter(skill_type=skill_type)
if proficiency:
    user_skills = user_skills.filter(proficiency_level=proficiency)
```

## Technical Implementation

### Models (`skills/models.py`)

**`SkillCategory`**
Top-level grouping. Seeded via `populate.py`.

```python
class SkillCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
```

**`Skill`**
The generic skill catalogue entry. Shared across all users.

```python
class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Normalise to title case before saving
        # Ensures "python", "Python", "PYTHON" all become "Python Programming"
        self.name = self.name.strip().title()
        super().save(*args, **kwargs)
```

**`UserSkill`**
The bridge table connecting a user to a skill with their specific metadata.

```python
class UserSkill(models.Model):
    SKILL_TYPE_CHOICES = [('offer', 'Offering'), ('request', 'Requesting')]
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPE_CHOICES)
    proficiency_level = models.CharField(max_length=15, choices=PROFICIENCY_CHOICES)
    years_of_experience = models.PositiveIntegerField(default=0)
    availability_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents adding the same skill+type combination twice
        unique_together = [('user', 'skill', 'skill_type')]
```

### Views (`skills/views.py`)

| View | Auth Needed | Purpose |
|---|---|---|
| `skill_list` | No | Browse all skills with search/filter |
| `add_user_skill` | Yes | Add a skill with two-form pattern |
| `my_skills` | Yes | View own skills |
| `skill_detail` | No | View single skill detail |
| `edit_user_skill` | Yes | Edit UserSkill metadata |
| `delete_user_skill` | Yes | Delete a UserSkill |

### Forms (`skills/forms.py`)

| Form | Purpose |
|---|---|
| `SkillForm` | Skill name, description, category |
| `UserSkillForm` | Skill type, proficiency, experience, availability |
| `SkillSearchForm` | Query, category, skill type, proficiency filters |

### Two-Form Pattern in add_user_skill

The add skill view handles two forms simultaneously: `SkillForm` for the generic skill data and `UserSkillForm` for the user's relationship to it:

```python
if skill_form.is_valid() and user_skill_form.is_valid():
    # Get or create the generic skill (case-insensitive match)
    skill, created = Skill.objects.get_or_create(
        name__iexact=skill_name,
        defaults={...}
    )
    # Create the user's specific relationship to the skill
    user_skill = user_skill_form.save(commit=False)
    user_skill.user = request.user
    user_skill.skill = skill
    user_skill.save()
```

`commit=False` holds the save so we can attach `user` and `skill` before writing to the database.

## URLs

| URL | Name | Auth Needed | Description |
|---|---|---|---|
| `/skills/` | `skills:list` | No | Browse all skills |
| `/skills/mine/` | `skills:my_skills` | Yes | Own skills |
| `/skills/add/` | `skills:add` | Yes | Add skill |
| `/skills/<pk>/` | `skills:detail` | No | Skill detail |
| `/skills/<pk>/edit/` | `skills:edit` | Yes | Edit skill |
| `/skills/<pk>/delete/` | `skills:delete` | Yes | Delete skill |

## Population Script (`populate.py`)

The population script seeds the database with initial data for development and testing. It uses a reusable helper function to add skills for multiple test users:

```python
def add_user_skills(user, skills_data):
    """Reusable helper — call once per user with their skills list"""
    for us_data in skills_data:
        skill = Skill.objects.get(name=us_data['skill_name'])
        UserSkill.objects.get_or_create(
            user=user,
            skill=skill,
            skill_type=us_data['skill_type'],
            defaults={...}
        )
```

`get_or_create` throughout means the script is safe to run multiple times without creating duplicates.

**Run with:**
```bash
python populate.py
```

## Key Design Decisions

### Why separate Skill and UserSkill?
If skill type lived on `Skill`, then "Python Programming" could only be either offered or requested globally. The separation means the same skill can be offered by Alice (advanced, 5 years) and requested by Bob (beginner) simultaneously.

### Why case-insensitive skill matching?
Without it, "python", "Python" and "PYTHON" create three separate database records. This fragments the skill catalogue, making search less effective and creating duplicate entries. `name__iexact` lookups combined with title-case normalisation on save ensures one canonical entry per skill.

### Why `SET_NULL` on category delete?
If a category is deleted, the skills in that category shouldn't be deleted too; they're still valid skills. `SET_NULL` preserves the skills while clearing the category reference, which can be reassigned later.

### Why `unique_together` on UserSkill?
A user offering Python AND requesting Python at the same time doesn't make sense. The constraint prevents this at the database level. Note that a user CAN offer Python (they're teaching) and separately request Spanish (they're learning).

## Known Limitations

- No pagination on the browse page - slow with large numbers of skills
- Skill description is optional but useful - no nudge to fill it in
- No skill endorsement system - can't verify someone actually has a skill
- Search is basic text matching - no fuzzy search or typo tolerance

## Future Improvements

- [ ] Pagination on browse page (25 skills per page) / continuous scroll
- [ ] Skill endorsements from swap partners
- [ ] Skill verification badges
- [ ] Fuzzy search with typo tolerance
- [ ] AI-suggested skill descriptions
- [ ] Skill popularity/demand indicators
- [ ] Related skills suggestions
- [ ] Skill difficulty ratings from the community