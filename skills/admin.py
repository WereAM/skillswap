from django.contrib import admin
from .models import Skill, SkillCategory, UserSkill

# Register your models here.
admin.site.register(Skill)
admin.site.register(SkillCategory)
admin.site.register(UserSkill)

