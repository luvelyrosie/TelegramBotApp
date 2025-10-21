from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.conf import settings
from .forms import TaskListForm, TaskForm
from .models import Task, TaskList
from .serializers import TaskSerializer, TaskListSerializer
from .permissions import IsOwnerOrBot
from accounts.models import Profile
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages


@login_required
def dashboard(request):
    tasklists = TaskList.objects.filter(created_by=request.user)
    return render(request, 'tasks/dashboard.html', {'tasklists': tasklists})


@login_required
def tasklist_detail(request, pk):
    tasklist = get_object_or_404(TaskList, pk=pk, created_by=request.user)
    tasks = Task.objects.filter(list=tasklist)
    return render(request, 'tasks/tasklist_detail.html', {'tasklist': tasklist, 'tasks': tasks})


@login_required
def tasklist_create(request):
    if request.method == 'POST':
        form = TaskListForm(request.POST)
        if form.is_valid():
            tasklist = form.save(commit=False)
            tasklist.created_by = request.user
            tasklist.save()
            return redirect('tasks:dashboard')
    else:
        form = TaskListForm()
    return render(request, 'tasks/tasklist_form.html', {'form': form, 'form_title': 'Create Task List'})


@login_required
def tasklist_edit(request, pk):
    tasklist = get_object_or_404(TaskList, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = TaskListForm(request.POST, instance=tasklist)
        if form.is_valid():
            form.save()
            return redirect('tasks:dashboard')
    else:
        form = TaskListForm(instance=tasklist)
    return render(request, 'tasks/tasklist_form.html', {'form': form, 'form_title': 'Edit Task List'})


@login_required
def tasklist_delete(request, pk):
    tasklist = get_object_or_404(TaskList, pk=pk, created_by=request.user)
    tasklist.delete()
    return redirect('tasks:dashboard')


@login_required
def task_create(request, tasklist_id):
    tasklist = get_object_or_404(TaskList, pk=tasklist_id, created_by=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.list = tasklist
            task.created_by = request.user
            task.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",
                {
                    "type": "task_update",
                    "payload": {
                        "id": task.id,
                        "title": task.title,
                        "is_done": task.is_done,
                        "created": True,
                        "assignee_id": getattr(task.assignee, "id", None),
                        "created_by_id": request.user.id,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "list_id": task.list.id,
                    },
                },
            )

            messages.success(request, f'Task "{task.title}" was created!')

            return redirect('tasks:tasklist_detail', pk=tasklist.id)
    else:
        form = TaskForm()

    return render(
        request,
        'tasks/task_form.html',
        {'form': form, 'form_title': 'Create Task', 'tasklist_id': tasklist.id},
    )

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task.objects.filter(Q(created_by=request.user) | Q(assignee=request.user)), pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",
                {
                    "type": "task_update",
                    "payload": {
                        "id": task.id,
                        "title": task.title,
                        "is_done": task.is_done,
                        "created": False,
                        "assignee_id": getattr(task.assignee, "id", None),
                        "created_by_id": task.created_by.id,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "list_id": task.list.id,
                    },
                },
            )

            return redirect('tasks:tasklist_detail', pk=task.list.id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'form_title': 'Edit Task', 'tasklist_id': task.list.id})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task.objects.filter(Q(created_by=request.user) | Q(assignee=request.user)), pk=pk)
    list_id = task.list.id
    task.delete()
    return redirect('tasks:tasklist_detail', pk=list_id)


@login_required
def task_mark_done(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_done = True
    task.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{request.user.id}",
        {
            "type": "task_update",
            "payload": {
                "id": task.id,
                "title": task.title,
                "is_done": task.is_done,
                "created": False,
                "assignee_id": getattr(task.assignee, "id", None),
                "created_by_id": task.created_by.id,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "list_id": task.list.id,
            },
        },
    )

    messages.success(request, f'Task "{task.title}" was marked as done!')

    return redirect('tasks:tasklist_detail', pk=task.list.id)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrBot]

    def get_queryset(self):
        qs = Task.objects.all()
        secret = self.request.headers.get("X-BOT-SECRET")

        if secret and secret == getattr(settings, "BOT_SHARED_SECRET", None):
            tg_id = self.request.query_params.get("assigned_to_tg")
            if tg_id:
                tg_id = int(tg_id)
                return qs.filter(assignee__profile__telegram_id=tg_id)

        user = self.request.user
        if user.is_authenticated:
            return qs.filter(models.Q(created_by=user) | models.Q(assignee=user)).distinct()

        return Task.objects.none()

    def partial_update(self, request, *args, **kwargs):
        secret = request.headers.get("X-BOT-SECRET")
        if secret and secret == getattr(settings, "BOT_SHARED_SECRET", None):
            instance = self.get_object()
            data = request.data
            if "is_done" in data:
                instance.is_done = data["is_done"]
                instance.save()
                return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
            return Response({"detail": "No updatable fields"}, status=status.HTTP_400_BAD_REQUEST)

        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="done")
    def mark_done(self, request, pk=None):
        secret = request.headers.get("X-BOT-SECRET")

        if secret and secret == getattr(settings, "BOT_SHARED_SECRET", None):
            task = get_object_or_404(Task.objects.all(), pk=pk)
            task.is_done = True
            task.save()
            return Response({"status": "done"}, status=200)

        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=401)

        task = self.get_object()
        if task.assignee == request.user or task.list.created_by == request.user:
            task.is_done = True
            task.save()
            return Response({"status": "done"}, status=200)

        return Response({"detail": "Permission denied."}, status=403)


class TaskListViewSet(viewsets.ModelViewSet):
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskList.objects.filter(created_by=self.request.user)


def live_tasks(request):
    return render(request, "tasks/live_tasks.html")