from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from runner_manager.models import HardwareInfo, RunnerInfo, Status
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
        # Make sure to define this URL name in urls.py
        self.url = reverse('add_new_runner')

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

    def test_get_hardware_authenticated(self):
        """Test successful hardware retrieval when user is authenticated"""
        # Login the user
        self.client.login(username='testuser', password='testpass123')

        # Create some test runners owned by the user
        runner1 = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='token1',
            state=Status.OFFLINE.value
        )
        runner2 = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='token2',
            state=Status.OFFLINE.value
        )

        # Create some test hardware associated with the runners
        hardware1 = HardwareInfo.objects.create(runner=runner1)
        hardware2 = HardwareInfo.objects.create(runner=runner2)

        # Make the GET request
        url = reverse('get_hardware')
        response = self.client.get(url)
        
        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check response content
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
        self.assertEqual(len(data['data']), 2)

        # Verify the hardware data
        hardware_ids = {str(hw['id']) for hw in data['data']}
        self.assertIn(str(hardware1.id), hardware_ids)
        self.assertIn(str(hardware2.id), hardware_ids)

    def test_get_hardware_unauthenticated(self):
        """Test hardware retrieval is rejected for unauthenticated users"""
        url = reverse('get_hardware')
        response = self.client.get(url)

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_get_hardware_wrong_method(self):
        """Test that only GET method is allowed"""
        # Login first
        self.client.login(username='testuser', password='testpass123')

        # Try POST request
        url = reverse('get_hardware')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

        # Verify error message
        data = response.json()
        self.assertEqual(data['error'], 'Only GET method is allowed')

    def test_get_hardware_other_user(self):
        """Test that user can only see their own runners' hardware"""
        # Login the first user
        self.client.login(username='testuser', password='testpass123')

        # Create another user with their own runner and hardware
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        # Create runners for both users
        user_runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='token1',
            state=Status.OFFLINE.value
        )
        other_runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=other_user,
            token='token2',
            state=Status.OFFLINE.value
        )

        # Create hardware for both runners
        user_hardware = HardwareInfo.objects.create(runner=user_runner)
        other_hardware = HardwareInfo.objects.create(runner=other_runner)

        # Make the GET request
        url = reverse('get_hardware')
        response = self.client.get(url)

        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should only see own hardware
        hardware_ids = {str(hw['id']) for hw in data['data']}
        self.assertIn(str(user_hardware.id), hardware_ids)
        self.assertNotIn(str(other_hardware.id), hardware_ids)
        self.assertEqual(len(data['data']), 1)
