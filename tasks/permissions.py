from rest_framework import permissions
from django.conf import settings

class IsOwnerOrBot(permissions.BasePermission):
    def has_permission(self, request, view):
        secret = request.headers.get("X-BOT-SECRET")
        if secret and secret == getattr(settings, "BOT_SHARED_SECRET", None):
            return True
        return bool(request.user and request.user.is_authenticated)