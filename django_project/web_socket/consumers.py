import json
from channels.generic.websocket import AsyncWebsocketConsumer


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('event_group', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('event_group', self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_event_update(self, event_data):
        await self.send(text_data=json.dumps(event_data))
