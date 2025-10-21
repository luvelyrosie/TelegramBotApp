from django.db import models
from django.conf import settings

class TaskList(models.Model):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasklists")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

class Task(models.Model):
    list = models.ForeignKey(TaskList, related_name="tasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="assigned_tasks", on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="created_tasks",on_delete=models.CASCADE, null=True,blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
