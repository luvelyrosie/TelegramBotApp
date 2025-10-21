from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "telegram_id", "bind_code")
    search_fields = ("user__username", "telegram_id")
