# Copyright (C) 2025 fyn-api Authors
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
#  see <https://www.gnu.org/licenses/>.

"""
Covers the runner installation/registration flow currently under active development:
- RunnerManagerUserViewSet.create - provisions a runner for an authenticated user.
- RunnerManagerRunnerViewSet.register - exchanges the initial id/token pair for a
  rotated token and activates the runner.

Other RunnerManagerRunnerViewSet endpoints (retrieve, partial_update, disabled list) predate
this work and are intentionally left uncovered here.
"""

import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from runner_manager.models import RunnerInfo, RunnerStatus


class RunnerManagerUserViewSetCreateTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpass123'
        )
        self.url = reverse('runner_manager_users-list')

    def test_create_rejected_for_authenticated_user_without_model_permission(self):
        """Known gap, not the behaviour this endpoint is meant to have: the view's
        DjangoModelPermissionsOrAnonReadOnly requires the Django model permission
        `runner_manager.add_runnerinfo`, which plain users are never granted anywhere in this
        codebase. This test documents current behaviour; it is not asserting this is correct."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {'name': 'my-runner'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(RunnerInfo.objects.exists())

    def test_create_unauthenticated_rejected(self):
        response = self.client.post(self.url, {'name': 'my-runner'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(RunnerInfo.objects.exists())

    def test_create_returns_runner_with_token(self):
        """A successful create must return the full serializer, including the initial token, so
        the caller can hand it to the runner for registration. Exercised via a superuser to
        route around the permission gap above and reach the view logic itself."""
        superuser = get_user_model().objects.create_superuser(
            username='admin', password='testpass123', email='admin@example.com'
        )
        self.client.force_authenticate(user=superuser)

        response = self.client.post(self.url, {'name': 'my-runner'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['name'], 'my-runner')
        self.assertEqual(data['state'], RunnerStatus.UNREGISTERED.value)
        self.assertTrue(data['token'])

        runner = RunnerInfo.objects.get(id=data['id'])
        self.assertEqual(runner.owner, superuser)
        self.assertEqual(runner.token, data['token'])
        self.assertEqual(runner.state, RunnerStatus.UNREGISTERED.value)

    def test_create_requires_name(self):
        """`name` no longer defaults to an empty string - a missing name must be rejected."""
        superuser = get_user_model().objects.create_superuser(
            username='admin', password='testpass123', email='admin@example.com'
        )
        self.client.force_authenticate(user=superuser)

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.json())


class RunnerManagerRunnerViewSetRegisterTests(APITestCase):

    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username='owner', password='testpass123'
        )
        self.url = reverse('runner_manager_runners-register')

    def test_register_success_rotates_token_and_activates(self):
        runner = RunnerInfo.objects.create(
            name='new-agent',
            owner=self.owner,
            token='initial-token',
            state=RunnerStatus.UNREGISTERED.value,
        )

        response = self.client.post(self.url, {'id': str(runner.id), 'token': 'initial-token'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], str(runner.id))
        self.assertNotEqual(data['token'], 'initial-token')

        runner.refresh_from_db()
        self.assertEqual(runner.state, RunnerStatus.IDLE.value)
        self.assertEqual(runner.token, data['token'])
        self.assertIsNotNone(runner.last_contact)

    def test_register_reregistration_rotates_token_again(self):
        """Re-running install against an already-registered runner (e.g. reinstall) should
        still succeed, using the most recently issued token."""
        runner = RunnerInfo.objects.create(
            name='existing-agent',
            owner=self.owner,
            token='current-token',
            state=RunnerStatus.IDLE.value,
        )

        response = self.client.post(self.url, {'id': str(runner.id), 'token': 'current-token'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        runner.refresh_from_db()
        self.assertNotEqual(runner.token, 'current-token')

    def test_register_missing_fields_rejected(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_wrong_token_rejected(self):
        runner = RunnerInfo.objects.create(
            name='new-agent',
            owner=self.owner,
            token='initial-token',
            state=RunnerStatus.UNREGISTERED.value,
        )

        response = self.client.post(self.url, {'id': str(runner.id), 'token': 'wrong-token'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        runner.refresh_from_db()
        self.assertEqual(runner.token, 'initial-token')
        self.assertEqual(runner.state, RunnerStatus.UNREGISTERED.value)

    def test_register_unknown_runner_id_rejected(self):
        response = self.client.post(self.url, {'id': str(uuid.uuid4()), 'token': 'anything'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_wrong_method_not_allowed(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_register_does_not_require_authentication(self):
        """register is the bootstrap step before the runner has any usable credentials, so it
        must succeed with no Authorization header at all."""
        runner = RunnerInfo.objects.create(
            name='anon-agent',
            owner=self.owner,
            token='tok',
            state=RunnerStatus.UNREGISTERED.value,
        )

        response = self.client.post(self.url, {'id': str(runner.id), 'token': 'tok'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
