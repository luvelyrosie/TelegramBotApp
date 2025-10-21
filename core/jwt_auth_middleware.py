from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from rest_framework_simplejwt.backends import TokenBackend
from channels.db import database_sync_to_async

User = get_user_model()

class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)
        self.token_backend = TokenBackend(algorithm="HS256", signing_key=settings.SECRET_KEY)

    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = scope.get("query_string", b"").decode()
        qs = parse_qs(query_string)
        token = None
        if "token" in qs:
            token = qs["token"][0]
        if token:
            try:
                validated = self.token_backend.decode(token, verify=True)
                user_id = validated.get("user_id")
                user = await self.get_user(user_id)
                scope["user"] = user or None
            except Exception:
                scope["user"] = None
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None