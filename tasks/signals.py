from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Task
from .tasks import send_telegram_notification_task

@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()

    payload = {
        "type": "task_update",
        "payload": {
            "id": instance.id,
            "title": instance.title,
            "is_done": instance.is_done,
            "assignee_id": instance.assignee_id,
            "created": created,
            "due_date": instance.due_date.isoformat() if instance.due_date else None,
            "created_by_id": instance.created_by_id if instance.created_by_id else None,
            "list_id": instance.list.id,
        }
    }

    if instance.assignee_id:
        async_to_sync(channel_layer.group_send)(f"user_{instance.assignee_id}", payload)
        message = f"New task assigned: {instance.title}" if created else f"Task updated: {instance.title}"
        send_telegram_notification_task.delay(instance.assignee_id, message)

    if instance.created_by_id and instance.created_by_id != instance.assignee_id:
        async_to_sync(channel_layer.group_send)(f"user_{instance.created_by_id}", payload)
        if created:
            send_telegram_notification_task.delay(instance.created_by_id, f"You created a new task: {instance.title}")

    if instance.due_date and not instance.is_done and instance.due_date > timezone.now():
        send_telegram_notification_task.apply_async(
            args=[instance.assignee_id, f"Overdue task: {instance.title} (due {instance.due_date})"],
            eta=instance.due_date
        )