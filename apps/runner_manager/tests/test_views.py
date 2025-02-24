from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from runner_manager.models import HardwareInfo, RunnerInfo, Status
import uuid
import json
import datetime


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

    # -------------------------------------------------------------------------
    # Test Front End API: add_runner
    # -------------------------------------------------------------------------

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
        self.assertEqual(runner.state, Status.UNREGISTERED.value)

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

    # -------------------------------------------------------------------------
    # Test Front End API: delete_runner
    # -------------------------------------------------------------------------

    def test_delete_runner(self):
        """Test successful runner deletion when user is authenticated"""
        # Login the user
        self.client.login(username='testuser', password='testpass123')

        # Create a test runner
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='token1',
            state=Status.OFFLINE.value
        )

        # Make the DELETE request
        url = reverse('delete_runner')
        response = self.client.delete(
            url,
            data=json.dumps({'id': str(runner.id)}),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')

        # Verify runner was deleted from database
        with self.assertRaises(RunnerInfo.DoesNotExist):
            RunnerInfo.objects.get(id=runner.id)

    def test_delete_runner_unauthenticated(self):
        """Test runner deletion is rejected for unauthenticated users"""
        # Create a test runner
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='token1',
            state=Status.OFFLINE.value
        )

        # Make the DELETE request without login
        url = reverse('delete_runner')
        response = self.client.delete(
            url,
            data=json.dumps({'id': str(runner.id)}),
            content_type='application/json'
        )

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

        # Verify runner still exists in database
        self.assertTrue(RunnerInfo.objects.filter(id=runner.id).exists())

    def test_delete_runner_no_id(self):
        """Test runner deletion is rejected when no ID is provided"""
        # Login the user
        self.client.login(username='testuser', password='testpass123')

        # Make the DELETE request with missing ID
        url = reverse('delete_runner')
        response = self.client.delete(
            url,
            data=json.dumps({}),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error'], 'Runner ID is required')

    def test_delete_runner_wrong_method(self):
        """Test that only DELETE method is allowed"""
        # Login first
        self.client.login(username='testuser', password='testpass123')

        # Try POST request
        url = reverse('delete_runner')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

        # Verify error message
        data = response.json()
        self.assertEqual(data['error'], 'Only DELETE method is allowed')

    def test_delete_runner_other_user(self):
        """Test that user can only delete their own runners"""
        # Login the first user
        self.client.login(username='testuser', password='testpass123')

        # Create another user with their own runner
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        # Create a runner owned by the other user
        other_runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=other_user,
            token='othertoken',
            state=Status.OFFLINE.value
        )

        # Try to delete the other user's runner
        url = reverse('delete_runner')
        response = self.client.delete(
            url,
            data=json.dumps({'id': str(other_runner.id)}),
            content_type='application/json'
        )

        # Should get a 403 Forbidden since the runner doesn't belong to the
        # authenticated user
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(
            data['message'], 'Permission denied: You do not own this runner')

        # Verify the runner still exists in database
        self.assertTrue(RunnerInfo.objects.filter(id=other_runner.id).exists())

    # -------------------------------------------------------------------------
    # Test Front End API: get_hardware
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Test Front End API: get_status
    # -------------------------------------------------------------------------

    def test_get_status_authenticated(self):
        """Test successful status retrieval when user is authenticated"""
        # Login the user
        self.client.login(username='testuser', password='testpass123')

        # Create some test runners owned by the user
        runners = [RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='token1',
            state=Status.BUSY.value,
            last_contact=timezone.now()
        ),
            RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='token2',
            state=Status.IDLE.value,
            last_contact=timezone.now()
        ), RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='token3',
            state=Status.OFFLINE.value,
        )]

        # Make the GET request
        url = reverse('get_status')
        response = self.client.get(url)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check response content
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
        self.assertEqual(len(data['data']), 3)

        # Verify the hardware data
        expected_states = {(str(r.id), r.state) for r in runners}
        received_states = {(r['id'], r['state']) for r in data['data']}
        self.assertEqual(expected_states, received_states)

    def test_get_status_unauthenticated(self):
        """Test status retrieval is rejected for unauthenticated users"""

        url = reverse('get_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_get_status_wrong_method(self):
        """Test that only GET method is allowed for get status"""

        # Login first
        self.client.login(username='testuser', password='testpass123')

        # Try POST request
        url = reverse('get_status')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

        # Verify error message
        data = response.json()
        self.assertEqual(data['error'], 'Only GET method is allowed')

    def test_get_status_other_user(self):
        """Test that only the user can get their own runners' state"""

        self.client.login(username='testuser', password='testpass123')
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

        # Make the GET request
        url = reverse('get_status')
        response = self.client.get(url)

        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['data']), 1)
        self.assertIn(str(user_runner.id), data['data'][0]['id'])
        self.assertNotIn(str(other_runner.id), data['data'][0]['id'])

    # -------------------------------------------------------------------------
    # Test Runner API: register
    # -------------------------------------------------------------------------

    def test_register_successful(self):
        """Test successful register valid token"""
        # Create a test runner
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='secret_token',
            state=Status.UNREGISTERED.value,
        )

        # Prepare and make PATCH valid request
        patch_data = {
            'id': str(runner.id),
            'token': 'secret_token'
        }
        url = reverse('register', args=[runner.id])
        response = self.client.post(
            url,
            data=json.dumps(patch_data),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['id'], str(runner.id))
        self.assertNotEqual(data['token'], 'secret_token')

        # Verify database was updated
        runner.refresh_from_db()
        self.assertEqual(runner.state, Status.IDLE.value)
        self.assertNotEqual(runner.token, 'secret_token')
        self.assertIsNotNone(runner.last_contact)

    def test_register_invalid_token(self):
        """Test register is rejected with invalid token"""
        # Create a test runner
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='secret_token',
            state=Status.UNREGISTERED.value,
        )

        # Prepare and make PATCH request with wrong token
        patch_data = {
            'id': str(runner.id),
            'token': 'wrong_token'
        }
        url = reverse('register', args=[runner.id])
        response = self.client.post(
            url,
            data=json.dumps(patch_data),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Authentication failed')

        # Verify database was not updated
        runner.refresh_from_db()
        self.assertEqual(runner.token, 'secret_token')
        self.assertEqual(runner.state, Status.UNREGISTERED.value)
        self.assertIsNone(runner.last_contact)

    def test_register_runner_not_found(self):
        """Test register non-existent runner ID"""
        # Generate a random UUID that doesn't exist
        non_existent_id = uuid.uuid4()
        patch_data = {
            'id': str(non_existent_id),
            'token': 'any_token'
        }

        # Make the PATCH request
        url = reverse('register', args=[non_existent_id])
        response = self.client.post(
            url,
            data=json.dumps(patch_data),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 404)

    def test_register_wrong_method(self):
        """Test that only POST method is allowed"""
        # Create a test runner
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='secret_token',
            state=Status.UNREGISTERED.value
        )

        # Try GET request
        url = reverse('register', args=[runner.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

        # Verify error message
        data = response.json()
        self.assertEqual(data['error'], 'Only POST method is allowed')

    # -------------------------------------------------------------------------
    # Test Runner API: report_status
    # -------------------------------------------------------------------------

    def test_report_status_successful(self):
        """Test successful status update with valid token and state"""
        # Create a test runner
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='secret_token',
            state=Status.IDLE.value,
            last_contact=timezone.now() - datetime.timedelta(minutes=10)
        )
        old_last_contact = runner.last_contact

        # Prepare and make PATCH valid request
        patch_data = {
            'token': 'secret_token',
            'state': Status.BUSY.value
        }
        url = reverse('report_status', args=[runner.id])
        response = self.client.patch(
            url,
            data=json.dumps(patch_data),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')

        # Verify database was updated
        runner.refresh_from_db()
        self.assertEqual(runner.state, Status.BUSY.value)
        self.assertGreater(runner.last_contact, old_last_contact)

    def test_report_status_runner_unregistered(self):
        """Test status update with non-existent runner ID"""
        # Create a test runner
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='secret_token',
            state=Status.UNREGISTERED.value,
        )

        # Prepare and make PATCH request with wrong token
        patch_data = {
            'token': 'secret_token',
            'state': Status.BUSY.value
        }
        url = reverse('report_status', args=[runner.id])
        response = self.client.patch(
            url,
            data=json.dumps(patch_data),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Unregistered runner')

        # Verify database was not updated
        runner.refresh_from_db()
        self.assertEqual(runner.token, 'secret_token')
        self.assertEqual(runner.state, Status.UNREGISTERED.value)

    def test_report_status_invalid_token(self):
        """Test status update is rejected with invalid token"""
        # Create a test runner
        time_now = timezone.now()
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='secret_token',
            state=Status.IDLE.value,
            last_contact=time_now
        )

        # Prepare and make PATCH request with wrong token
        patch_data = {
            'token': 'wrong_token',
            'state': Status.BUSY.value
        }
        url = reverse('report_status', args=[runner.id])
        response = self.client.patch(
            url,
            data=json.dumps(patch_data),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Authentication failed')

        # Verify database was not updated
        runner.refresh_from_db()
        self.assertEqual(runner.token, 'secret_token')
        self.assertEqual(runner.state, Status.IDLE.value)
        self.assertEqual(runner.last_contact, time_now)

    def test_report_status_invalid_state(self):
        """Test status update is rejected with invalid state"""
        # Create a test runner
        time_now = timezone.now()
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='secret_token',
            state=Status.IDLE.value,
            last_contact=time_now
        )

        # Prepare and make PATCH request with invalid state
        patch_data = {
            'token': 'secret_token',
            'state': 'invalid_state'
        }
        url = reverse('report_status', args=[runner.id])
        response = self.client.patch(
            url,
            data=json.dumps(patch_data),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn(data['status'], 'error')

        # Verify database was NOT updated
        runner.refresh_from_db()
        self.assertEqual(runner.token, 'secret_token')
        self.assertEqual(runner.state, Status.IDLE.value)
        self.assertEqual(runner.last_contact, time_now)

    def test_report_status_runner_not_found(self):
        """Test status update with non-existent runner ID"""
        # Generate a random UUID that doesn't exist
        non_existent_id = uuid.uuid4()
        patch_data = {
            'token': 'any_token',
            'state': Status.BUSY.value
        }

        # Make the PATCH request
        url = reverse('report_status', args=[non_existent_id])
        response = self.client.patch(
            url,
            data=json.dumps(patch_data),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 404)

    def test_report_status_wrong_method(self):
        """Test that only PATCH method is allowed"""
        # Create a test runner
        runner = RunnerInfo.objects.create(
            id=uuid.uuid4(),
            owner=self.user,
            token='secret_token',
            state=Status.IDLE.value,
            last_contact=timezone.now() - datetime.timedelta(minutes=10)
        )

        # Try GET request
        url = reverse('report_status', args=[runner.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

        # Verify error message
        data = response.json()
        self.assertEqual(data['error'], 'Only PATCH method is allowed')
