from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from skills.models import Skill, SkillCategory, UserSkill
from swaps.models import SwapRequests, Session, Review

# Create your tests here.

class SwapTests(TestCase):
    # Create two users with skills so we can test the full swap flow between them
    def setUp(self):
        self.client = Client()

        # Create two users
        self.sender = User.objects.create_user(
            username='sender',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.sender)
        UserProfile.objects.create(user=self.receiver)

        # Create skills
        self.category = SkillCategory.objects.create(name='Technology')
        self.skill1 = Skill.objects.create(name='Python', category=self.category)
        self.skill2 = Skill.objects.create(name='Guitar', category=self.category)

        # Sender offers Python, receiver offers Guitar
        self.sender_skill = UserSkill.objects.create(
            user=self.sender,
            skill=self.skill1,
            skill_type='offer',
            proficiency_level='advanced',
        )
        self.receiver_skill = UserSkill.objects.create(
            user=self.receiver,
            skill=self.skill2,
            skill_type='offer',
            proficiency_level='intermediate',
        )

        # Create a base swap request for tests that need one
        self.swap = SwapRequests.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            offered_skill=self.sender_skill,
            requested_skill=self.receiver_skill,
            status='pending',
            message='Hi, want to swap?'
        )

    # Swap creation page should load for authenticated users
    def test_create_swap_page_loads(self):
        self.client.login(username='sender', password='testpass123')
        response = self.client.get(
            reverse('swaps:create',
            kwargs={'skill_id': self.receiver_skill.pk})
        )
        self.assertEqual(response.status_code, 200)

    # Received requests/Inbox should load for authenticated users
    def test_inbox_loads(self):
        self.client.login(username='receiver', password='testpass123')
        response = self.client.get(reverse('swaps:inbox'))
        self.assertEqual(response.status_code, 200)

    # Inbox should show requests sent to the logged in user
    def test_inbox_shows_received_requests(self):
        self.client.login(username='receiver', password='testpass123')
        response = self.client.get(reverse('swaps:inbox'))
        self.assertContains(response, 'sender')

    # Sent requests page should load
    def test_sent_requests_loads(self):
        self.client.login(username='sender', password='testpass123')
        response = self.client.get(reverse('swaps:sent'))
        self.assertEqual(response.status_code, 200)

    # Receiver should be able to accept a pending swap
    def test_accept_swap(self):
        self.client.login(username='receiver', password='testpass123')
        self.client.post(reverse('swaps:accept', kwargs={'pk': self.swap.pk}))
        self.swap.refresh_from_db()
        self.assertEqual(self.swap.status, 'accepted')

    # Receiver should be able to deny a pending swap
    def test_deny_swap(self):
        self.client.login(username='receiver', password='testpass123')
        self.client.post(reverse('swaps:deny', kwargs={'pk': self.swap.pk}))
        self.swap.refresh_from_db()
        self.assertEqual(self.swap.status, 'rejected')

    # Sender should be able to cancel a pending swap
    def test_cancel_swap(self):
        self.client.login(username='sender', password='testpass123')
        self.client.post(reverse('swaps:cancel', kwargs={'pk': self.swap.pk}))
        self.swap.refresh_from_db()
        self.assertEqual(self.swap.status, 'cancelled')