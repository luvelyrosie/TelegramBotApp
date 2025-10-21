from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from .models import Profile
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


User=get_user_model()

def index(request):
    bind_info = None
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.bind_code:
            profile.generate_bind_code()
        bind_info = {
            "username": request.user.username,
            "telegram_id": profile.telegram_id,
            "bind_code": profile.bind_code
        }
    return render(request, "index.html", {"bind_info": bind_info})

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class RequestBindCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        code = profile.generate_bind_code()
        return Response({"bind_code": code})

class BotBindView(APIView):
    permission_classes = []
    def post(self, request):
        secret = request.headers.get("X-BOT-SECRET")
        if secret != settings.BOT_SHARED_SECRET:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        code = request.data.get("code")
        telegram_id = request.data.get("telegram_id")
        if not code or not telegram_id:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)
        profile = get_object_or_404(Profile, bind_code=code)
        profile.telegram_id = telegram_id
        profile.bind_code = None
        profile.save(update_fields=["telegram_id", "bind_code"])
        return Response({"status": "ok"})

class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        qs = super().get_queryset()
        username = self.request.query_params.get("username")
        if username:
            qs = qs.filter(username__icontains=username)
        return qs
    
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

class MyBindInfoView(APIView):
    permission_classes = [IsAuthenticated]
    
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.bind_code:
            profile.generate_bind_code()
        return Response({
            "username": request.user.username,
            "telegram_id": profile.telegram_id,
            "bind_code": profile.bind_code
        })