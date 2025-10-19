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

import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from runner_manager.models import RunnerInfo
from django.core.exceptions import ObjectDoesNotExist


class RunnerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.runner_id = self.scope["url_route"]["kwargs"]["runner_id"]
        self.runner_group_name = f"runner_{self.runner_id}"
        self.joined_group = False
        
        try:
            runner = await self.get_runner(self.runner_id)
            token = self.get_token_from_headers()

            if token and token == runner.token:
                # Join runner-specific group
                await self.channel_layer.group_add(
                    self.runner_group_name,
                    self.channel_name
                )
                self.joined_group = True
                await self.accept()
            else:
                await self.close()

        except ObjectDoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        # Leave runner-specific group
        if self.joined_group:
            await self.channel_layer.group_discard(
                self.runner_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.send(text_data=json.dumps({"message": message}))

    # Handler for job notifications from channel layer
    async def job_notification(self, event):
        """
        Receives job_notification events from channel layer.
        This is called when channel_layer.group_send() is used.
        """
        # Send message to WebSocket client
        await self.send(text_data=json.dumps({
            'id': str(uuid.uuid4()),
            'type': 'new_job',
            'job_id': event['job_id'],
            'message': event.get('message', 'New job available')
        }))

    def get_token_from_headers(self):
        """Extract token from headers"""
        for header_name, header_value in self.scope["headers"]:
            if header_name.decode("utf-8") == "token":
                return header_value.decode("utf-8")
        return None

    @database_sync_to_async
    def get_runner(self, runner_id):
        return RunnerInfo.objects.get(id=runner_id)
