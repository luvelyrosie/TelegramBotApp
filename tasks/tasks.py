from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings
import requests
from .models import Task
from django.utils import timezone

User = get_user_model()

@shared_task
def send_telegram_notification_task(user_id, message):
    try:
        user = User.objects.get(pk=user_id)
        profile = getattr(user, "profile", None)
        if not profile or not profile.telegram_id:
            return
        tg_id = profile.telegram_id
    except User.DoesNotExist:
        return

    url = settings.BOT_API_BASE.rstrip("/") + "/send/"
    headers = {"X-BOT-SECRET": settings.BOT_SHARED_SECRET}
    payload = {"telegram_id": tg_id, "message": message}
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception:
        pass

@shared_task
def check_overdue_tasks():
    now = timezone.localtime(timezone.now())
    overdue = Task.objects.filter(is_done=False, due_date__lt=now, notified=False)
    for t in overdue:
        if t.assignee_id:
            send_telegram_notification_task.delay(
                t.assignee_id,
                f"Overdue task: {t.title} (due {t.due_date})"
            )
        t.notified = True
        t.save(update_fields=['notified'])