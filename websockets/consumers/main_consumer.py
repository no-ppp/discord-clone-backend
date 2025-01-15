from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class MainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscription = set()
    
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()
        await database_sync_to_async(self.user.go_online)()
        await self.channel_layer.group_add('status_updates', self.channel_name)
        await self.send(json.dumps({
            'type': 'status_update',
            'status': 'online',
            'user_id': self.user.id,
        }))
    
    async def disconnect(self, close_code):
        await database_sync_to_async(self.user.go_offline)()
        await self.channel_layer.group_discard('status_updates', self.channel_name)
        await self.send(json.dumps({
            'type': 'status_update',
            'status': 'offline',
            'user_id': self.user.id,
        }))
        await self.close()
