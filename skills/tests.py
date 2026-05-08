from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from skills.models import Skill, SkillCategory, UserSkill

# Create your tests here.

class SkillTests(TestCase):
    def setUp(self):
        # Create test user, category and skill for reuse across tests
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = SkillCategory.objects.create(
            name='Technology',
            description='Tech skills'
        )
        self.skill = Skill.objects.create(
            name='Python',
            category=self.category,
        )
        self.user_skill = UserSkill.objects.create(
            user=self.user,
            skill=self.skill,
            skill_type='offer',
            proficiency_level='advanced',
            years_of_experience=3,
        )

    # Browse skills page should load for anyone
    def test_skill_list_loads(self):
        response = self.client.get(reverse('skills:list'))
        self.assertEqual(response.status_code, 200)

    # Browse skills page should contain the test skill
    def test_skill_list_shows_skills(self):
        response = self.client.get(reverse('skills:list'))
        self.assertContains(response, 'Python')

    # Add skill page should redirect unauthenticated users to login
    def test_add_skill_requires_login(self):
        response = self.client.get(reverse('skills:add'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    # Adding a skill should create a new UserSkill object
    def test_add_skill(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('skills:add'),
            {
                'name': 'Django',
                'description': 'Web framework',
                'category': self.category.pk,
                'skill_type': 'offer',
                'proficiency_level': 'intermediate',
                'years_of_experience': 2,
                'availability_description': 'Weekends',
            })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Skill.objects.filter(name='Django').exists())

    # My skills page should load for authenticated users
    def test_my_skills_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('skills:my_skills'))
        self.assertEqual(response.status_code, 200)

    # My skills page should only show the logged in user's skills
    def test_my_skills_shows_only_own_skills(self):
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        other_skill = Skill.objects.create(name='Knitting', category=self.category)
        UserSkill.objects.create(
            user=other_user,
            skill=other_skill,
            skill_type='offer',
            proficiency_level='beginner',
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('skills:my_skills'))
        self.assertContains(response, 'Python')
        self.assertNotContains(response, 'Knitting')

    # Skill detail page should load for authenticated users
    def test_skill_detail_loads(self):
        response = self.client.get(
            reverse('skills:detail',
            kwargs={'pk': self.user_skill.pk})
        )
        self.assertEqual(response.status_code, 200)

    # A user should not be able to edit another user's skills
    def test_edit_skill_requires_ownership(self):
        other_user = User.objects.cretae_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(
            reverse('skills:edit',
            kwargs={'pk': self.user_skill.pk})
        )
        self.assertEqual(response.status_code, 404)

    # Deleting a skill should remove it from the database"""
    def test_delete_skill(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('skills:delete',
            kwargs={'pk': self.user_skill.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserSkill.objects.filter(pk=self.user_skill.pk).exists())

    # Searching by skill name should return the matching skill
    def test_search_skills(self):
        response = self.client.get(reverse('skills:list'), {'query': "Python"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')

    # Filtering skills by category should return matching skills
    def test_filter_by_category(self):
        response = self.client.get(
            reverse('skills:list'),
            {'category': self.category.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')