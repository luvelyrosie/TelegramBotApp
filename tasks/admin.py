from django.contrib import admin
from .models import TaskList, Task

@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "list", "assignee", "due_date", "is_done")
    list_filter = ("is_done",)