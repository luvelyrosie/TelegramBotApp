# core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from tasks.views import TaskViewSet, TaskListViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import index

# DRF router for API endpoints
router = routers.DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"lists", TaskListViewSet, basename="lists")

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API
    path("api/", include(router.urls)),

    # JWT
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Accounts app for registration/login pages
    path("accounts/", include("accounts.urls")),
    
    path("tasks/", include(("tasks.urls", "tasks"), namespace="tasks")),

    # Front
    path("", index, name="index"),
]