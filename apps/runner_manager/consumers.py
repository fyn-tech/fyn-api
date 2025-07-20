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
from channels.generic.websocket import AsyncWebsocketConsumer
from runner_manager.models import RunnerInfo
from django.core.exceptions import ObjectDoesNotExist


class RunnerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        runner_id = self.scope["url_route"]["kwargs"]["runner_id"]
        try:
            runner = await RunnerInfo.objects.aget(id=runner_id)
            token = None
            for tuple in self.scope["headers"]:
                if tuple[0].decode("utf-8") == "token":
                    token = tuple[1].decode("utf-8")

            if token and token == runner.token:
                await self.accept()
            else:
                await self.close()

        except ObjectDoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.send(text_data=json.dumps({"message": message}))
