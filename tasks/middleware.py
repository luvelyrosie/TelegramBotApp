from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.conf import settings
from django.db import close_old_connections

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.backends import TokenBackend

        User = get_user_model()
        close_old_connections()

        token_backend = TokenBackend(algorithm="HS256", signing_key=settings.SECRET_KEY)

        query_string = scope.get("query_string", b"").decode()
        from urllib.parse import parse_qs
        qs = parse_qs(query_string)
        token = qs.get("token", [None])[0]

        if token:
            try:
                validated = token_backend.decode(token, verify=True)
                user_id = validated.get("user_id")
                user = await self.get_user(user_id, User)
                scope["user"] = user or AnonymousUser()
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id, User):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None