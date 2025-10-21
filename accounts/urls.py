from django.urls import path
from .views import (
    RegisterView, RequestBindCodeView, BotBindView, UserListView, register, MyBindInfoView
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Front
    path('register/', register, name='register'),  

    # Login logout
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # API
    path("api/register/", RegisterView.as_view(), name="api_register"),
    path("api/bind/request/", RequestBindCodeView.as_view(), name="bind_request"),
    path("api/bot/bind/", BotBindView.as_view(), name="bot_bind"),
    path("api/users/", UserListView.as_view(), name="users_list"),
    path("api/mybindinfo/", MyBindInfoView.as_view(), name="my_bind_info"),
]