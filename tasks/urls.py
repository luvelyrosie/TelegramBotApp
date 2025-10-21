from django.urls import path, include
from .views import dashboard
from rest_framework import routers
from .views import TaskViewSet, TaskListViewSet
from . import views
from .views import tasklist_detail, tasklist_create, tasklist_edit, tasklist_delete
from .views import task_create, task_edit, task_delete, task_mark_done

router = routers.DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"lists", TaskListViewSet, basename="lists")

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Task List
    path("tasklist/create/", tasklist_create, name="tasklist_create"),
    path("tasklist/<int:pk>/", tasklist_detail, name="tasklist_detail"),
    path("tasklist/<int:pk>/edit/", tasklist_edit, name="tasklist_edit"),
    path("tasklist/<int:pk>/delete/", tasklist_delete, name="tasklist_delete"),

    # Task
    path("task/<int:tasklist_id>/create/", task_create, name="task_create"),
    path("task/<int:pk>/edit/", task_edit, name="task_edit"),
    path("task/<int:pk>/delete/", task_delete, name="task_delete"),
    path("task/<int:pk>/done/", task_mark_done, name="task_mark_done"),
    
    path("api/", include(router.urls)),
    path("live/", views.live_tasks, name="live_tasks"),
]