from django.db import models
from django.conf import settings
import secrets
from django.contrib.auth.models import AbstractUser

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    bind_code = models.CharField(max_length=64, null=True, blank=True)

    def generate_bind_code(self):
        code = secrets.token_urlsafe(8)
        self.bind_code = code
        self.save(update_fields=["bind_code"])
        return code

    def __str__(self):
        return f"Profile({self.user.username})"

class User(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.username