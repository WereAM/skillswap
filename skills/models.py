from django.db import models
from django.contrib.auth.models import User

class SkillCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Skill Categories'

class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class UserSkill(models.Model):
    OFFERING = 'offer'
    REQUESTING = 'request'

    SKILL_TYPE_CHOICES = [
        (OFFERING, 'Offering'),
        (REQUESTING, 'Requesting'),
    ]

    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERT = 'expert'

    PROFICIENCY_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
        (EXPERT, 'Expert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPE_CHOICES)
    proficiency_level = models.CharField(
        max_length=15,
        choices=PROFICIENCY_CHOICES,
        blank=True
    )

    years_of_experience = models.PositiveIntegerField(default=0)
    availability_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.skill.name} ({self.skill_type})'
    
    # prevent a user from entering the same skill and skilltype twice
    class Meta:
        unique_together = ('user', 'skill', 'skill_type')