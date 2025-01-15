from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
import json
import redis

class MainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis(host='127.0.0.1', port=6379, db=1)

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
            
        await self.accept()
        
        # Dodaj użytkownika do Redis
        await database_sync_to_async(self.add_user_to_group)()
        
        # Pobierz aktualnych użytkowników
        current_users = await database_sync_to_async(self.get_group_users)()
        
        await self.channel_layer.group_add('status_updates', self.channel_name)
        await database_sync_to_async(self.user.go_online)()
        
        # Wyślij listę użytkowników
        await self.send(text_data=json.dumps({
            'type': 'group_users',
            'users': list(current_users)
        }))
        
        # Broadcast nowego statusu
        await self.channel_layer.group_send(
            'status_updates',
            {
                'type': 'broadcast_status',
                'user_id': self.user.id,
                'status': 'online'
            }
        )

    def add_user_to_group(self):
        self.redis_client.sadd('group_users', self.user.id)
    
    def get_group_users(self):
        users = self.redis_client.smembers('group_users')
        return [int(user_id) for user_id in users]  # Konwertuj bytes na int
    
    def remove_user_from_group(self):
        self.redis_client.srem('group_users', self.user.id)

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await database_sync_to_async(self.remove_user_from_group)()
            await database_sync_to_async(self.user.go_offline)()
            await self.channel_layer.group_send(
                'status_updates',
                {
                    'type': 'broadcast_status',
                    'user_id': self.user.id,
                    'status': 'offline'
                }
            )
        await self.channel_layer.group_discard('status_updates', self.channel_name)

    # Dodajemy handler dla broadcast_status
    async def broadcast_status(self, event):
        """
        Handler dla wiadomości typu broadcast_status.
        Wysyła wiadomość do klienta WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'user_id': event['user_id'],
            'status': event['status']
        }))