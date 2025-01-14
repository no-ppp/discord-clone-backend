from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("Próba połączenia WebSocket")
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Ustaw użytkownika jako online
        await self.update_user_status(self.user.id, 'online')

        # Dołącz do grupy statusów
        await self.channel_layer.group_add(
            'status_updates',
            self.channel_name
        )

        

        await self.accept()
        
        # Wyślij początkowe statusy wszystkich użytkowników
        statuses = await self.get_all_statuses()
        await self.send(text_data=json.dumps({
            'type': 'initial_statuses',
            'statuses': statuses
        }))

    @database_sync_to_async
    def get_all_statuses(self):
        """Pobierz statusy wszystkich użytkowników"""
        statuses = {}
        for user in User.objects.all():
            statuses[str(user.id)] = {
                'status': user.status,
                'is_online': user.is_online,
                'last_online': user.last_online.isoformat() if user.last_online else None
            }
        return statuses

    @database_sync_to_async
    def update_user_status(self, user_id, status):
        """Aktualizuj status użytkownika"""
        try:
            user = User.objects.get(id=user_id)
            user.set_status(status)
            logger.info(f"Zaktualizowano status użytkownika {user_id} na {status}")
            return True
        except User.DoesNotExist:
            logger.error(f"Nie znaleziono użytkownika o ID {user_id}")
            return False

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'status_update':
                await self.handle_status_update(data)
            else:
                logger.warning(f"Nieznany typ wiadomości: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Otrzymano nieprawidłowy format JSON")
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania wiadomości: {str(e)}")

    async def handle_status_update(self, data):
        """Obsługa aktualizacji statusu"""
        user_id = data.get('user_id')
        status = data.get('status')
        
        if user_id and status:
            # Sprawdź czy status jest prawidłowy
            if status not in dict(User.STATUS_CHOICES):
                logger.error(f"Nieprawidłowy status: {status}")
                return

            # Aktualizuj status w bazie danych
            success = await self.update_user_status(user_id, status)
            
            if success:
                # Pobierz zaktualizowane dane użytkownika
                user_data = await self.get_user_status(user_id)
                
                # Wyślij aktualizację do wszystkich
                await self.channel_layer.group_send(
                    'status_updates',
                    {
                        'type': 'status_message',
                        'user_id': user_id,
                        'status_data': user_data
                    }
                )

    @database_sync_to_async
    def get_user_status(self, user_id):
        """Pobierz aktualny status użytkownika"""
        user = User.objects.get(id=user_id)
        return {
            'status': user.status,
            'is_online': user.is_online,
            'last_online': user.last_online.isoformat()
        }

    async def status_message(self, event):
        """Odbieranie i wysyłanie aktualizacji statusu"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'user_id': event['user_id'],
            'status_data': event['status_data']
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            # Ustaw użytkownika jako offline
            await self.update_user_status(self.user.id, 'offline')
            
            # Powiadom innych o zmianie statusu
            user_data = await self.get_user_status(self.user.id)
            await self.channel_layer.group_send(
                'status_updates',
                {
                    'type': 'status_message',
                    'user_id': self.user.id,
                    'status_data': user_data
                }
            )

        # Opuść grupę statusów
        await self.channel_layer.group_discard(
            'status_updates',
            self.channel_name
        )