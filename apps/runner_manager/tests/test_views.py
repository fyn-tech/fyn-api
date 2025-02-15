from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import RunnerInfo, Status
import uuid

class RunnerViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        # URL for the add_new_runner view
        self.url = reverse('add_new_runner')  # Make sure to define this URL name in urls.py

    def test_add_runner_authenticated(self):
        """Test successful runner creation when user is authenticated"""
        # Log in the user
        self.client.login(username='testuser', password='testpass123')
        
        # Make the POST request
        response = self.client.post(self.url)
        
        # Check response status code
        self.assertEqual(response.status_code, 201)
        
        # Check response content
        data = response.json()
        self.assertIn('id', data)
        self.assertIn('token', data)
        
        # Verify that the UUID is valid
        try:
            uuid.UUID(data['id'])
        except ValueError:
            self.fail("ID is not a valid UUID")
        
        # Check that token is not empty
        self.assertTrue(data['token'])
        
        # Verify runner was created in database
        runner = RunnerInfo.objects.get(id=data['id'])
        self.assertEqual(runner.owner, self.user)
        self.assertEqual(runner.token, data['token'])
        self.assertEqual(runner.state, Status.OFFLINE.value)

    def test_add_runner_unauthenticated(self):
        """Test runner creation is rejected for unauthenticated users"""
        response = self.client.post(self.url)
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))  # Adjust path as needed

    def test_add_runner_wrong_method(self):
        """Test that only POST method is allowed"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Try GET request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        
        # Verify error message
        data = response.json()
        self.assertEqual(data['error'], 'Only POST method is allowed')