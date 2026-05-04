import os

# direct the script to the settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillswap.settings')

import django
django.setup()

# import models
from django.contrib.auth.models import User
from skills.models import Skill, SkillCategory, UserSkill

def add_user_skills(user, skills_data):
    """Helper function to add skills to a user, reusable for any user"""
    for us_data in skills_data:
        skill = Skill.objects.get(name=us_data['skill_name'])
        user_skill, created = UserSkill.objects.get_or_create(
            user=user,
            skill=skill,
            skill_type=us_data['skill_type'],
            defaults={
                'proficiency_level': us_data['proficiency_level'],
                'years_of_experience': us_data['years_of_experience'],
                'availability_description': us_data['availability_description'],
            }
        )
        status = "Created" if created else "Already exists"
        print(f"  {status}: {user.username} - {skill.name} ({us_data['skill_type']})")


def populate():
    categories = [
        {
            'name': 'Software Development',
            'description': 'Programming, database and UI design skills'
        },
        {
            'name': 'Language',
            'description': 'Speaking, writing and translation skills'
        },
        {
            'name': 'Music',
            'description': 'Instruments, singing and music production'
        },
        {
            'name': 'Cooking',
            'description': 'Cuisines, baking and nutrition'
        },
        {
            'name': 'Fitness',
            'description': 'Exercise, yoga, sports and wellbeing'
        },
        {
            'name': 'Art & Design',
            'description': 'Drawing, painting, graphic design and photography'
        },
        {
            'name': 'Academic',
            'description': 'Tutoring, research and study skills'
        },
        {
            'name': 'Other',
            'description': 'Everything else!'
        },
    ]

    skills = [
        {'name': 'Python Programming', 'category': 'Software Development', 'difficulty_level': 'Intermediate'},
        {'name': 'Web Development', 'category': 'Software Development', 'difficulty_level': 'Intermediate'},
        {'name': 'Spanish', 'category': 'Language', 'difficulty_level': 'Beginner'},
        {'name': 'French', 'category': 'Language', 'difficulty_level': 'Beginner'},
        {'name': 'Guitar', 'category': 'Music', 'difficulty_level': 'Beginner'},
        {'name': 'Piano', 'category': 'Music', 'difficulty_level': 'Intermediate'},
        {'name': 'Baking', 'category': 'Cooking', 'difficulty_level': 'Beginner'},
        {'name': 'Italian Cuisine', 'category': 'Cooking', 'difficulty_level': 'Advanced'},
        {'name': 'Yoga', 'category': 'Fitness', 'difficulty_level': 'Beginner'},
        {'name': 'Photography', 'category': 'Art & Design','difficulty_level': 'Intermediate'},
        {'name': 'Maths Tutoring', 'category': 'Academic', 'difficulty_level': 'Advanced'},
        {'name': 'Knitting', 'category': 'Other', 'difficulty_level': 'Beginner'},
    ]

    print("Seeding categories...")
    for cat_data in categories:
        category, created = SkillCategory.objects.get_or_create(
            name = cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        status = "Created" if created else "Already exists"
        print(f" {status} : {category.name}")

    print("n\Seeding skills...")
    for skill_data in skills:
        category = SkillCategory.objects.get(name=skill_data['category'])
        skill, created = Skill.objects.get_or_create(
            name = skill_data['name'],
            defaults={
                'category': category,
                'difficulty_level': skill_data['difficulty_level'],
            }
        )
        status = "Created" if created else "Already exists"
        print(f" {status}: {skill.name}")

    print("n\Done! Database seeded successfully.")

   # Create test users
    test_user1, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@skillswap.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    if created:
        test_user1.set_password('password123')
        test_user1.save()

    test_user2, created = User.objects.get_or_create(
        username='testuser2',
        defaults={'email': 'test2@skillswap.com', 'first_name': 'Test2', 'last_name': 'User'}
    )
    if created:
        test_user2.set_password('password123')
        test_user2.save()

    # Define skills per user
    user1_skills = [
        {'skill_name': 'Python Programming', 'skill_type': 'offer',
         'proficiency_level': 'advanced', 'years_of_experience': 3,
         'availability_description': 'Weekday evenings'},
        {'skill_name': 'Spanish', 'skill_type': 'request',
         'proficiency_level': 'beginner', 'years_of_experience': 0,
         'availability_description': 'Weekends'},
    ]

    user2_skills = [
        {'skill_name': 'Piano', 'skill_type': 'offer',
         'proficiency_level': 'advanced', 'years_of_experience': 5,
         'availability_description': 'Weekends only'},
        {'skill_name': 'Python Programming', 'skill_type': 'request',
         'proficiency_level': 'beginner', 'years_of_experience': 0,
         'availability_description': 'Flexible'},
    ]

    # Seed skills for each user using the helper function
    print("\nSeeding user skills...")
    add_user_skills(test_user1, user1_skills)
    add_user_skills(test_user2, user2_skills)

    print("\nDone!")

if __name__ == '__main__':
    populate()
