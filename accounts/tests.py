from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile

# Create your tests here.

class AuthTest(TestCase):
    # setUp to create a reusable test client
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username = 'testuser',
            email = 'test@test.com',
            password = 'testpass123'
        )
        UserProfile.objects.create(user=self.user)

    # test registration page exists - return 200 (OK)
    def test_register_page_loads(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    # registering a user with valid data should create a user and redirect them to login
    def test_register_new_user(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@test.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        # check redirect
        self.assertEqual(response.status_code, 302)
        # check the database value
        self.assertTrue(User.objects.filter(username='newuser').exists())

    # logging in with correct credentials should redirect to the profile page
    def test_login_valid_credentials(self): 
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    # logging in with the wrong password should stay on the login page
    def test_login_invalid_credentials(self): 
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        # re-render login
        self.assertEqual(response.status_code, 200)
    
    # Profile page should load for authenticated users
    def test_profile_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    # Profile page should redirect unauthenticated users to login
    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    # Editing profile should update bio and location
    def test_edit_profile(self):
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:edit_profile'), {
            'bio': 'I love teaching Python!',
            'location': 'Glasgow',
        })
        # Should redirect after saving
        self.assertEqual(response.status_code, 302)
        # Check the data was saved
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.bio, 'I love teaching Python!')
        self.assertEqual(profile.location, 'Glasgow')

    # Public profile pages should be visible for all users
    def test_public_profile_loads(self):
        response = self.client.get(
            reverse('accounts:public_profile',
            kwargs={'username': 'testuser'})
        )
        self.assertEqual(response.status_code, 200)

    # Public profile should return error 404 for users that don't exist
    def test_public_profile_404_for_nonexistent_users(self):
        respone = self.client.get(
            reverse('accounts:public_profile',
            kwargs={'username': 'doesnotexist'})
        )
        self.assertEqual(response.status_code, 404)
