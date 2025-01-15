from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs

User = get_user_model()


class JWTAuthenticationMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        
        scope['user'] = AnonymousUser()
        
        query_string = scope.get('query_string', b'').decode()
        token = None
        if 'token=' in query_string:
            token = query_string.split('token=')[1]
        if token:
            try:
                validate_token = AccessToken(token)
                user_id = validate_token['user_id']
                scope['user'] = await self.get_user(user_id)
            except:
                pass
            
            return await super().__call__(scope, receive, send)
        
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()