import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Profile
from django.shortcuts import get_object_or_404

BOT_SECRET = os.getenv("BOT_SHARED_SECRET", "default-secret")

class BotBindView(APIView):
    permission_classes = []

    def post(self, request):
        if request.headers.get("X-BOT-SECRET") != BOT_SECRET:
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)

        code = request.data.get("code")
        telegram_id = request.data.get("telegram_id")
        if not code or not telegram_id:
            return Response({"detail": "missing"}, status=status.HTTP_400_BAD_REQUEST)

        profile = get_object_or_404(Profile, bind_code=code)
        profile.telegram_id = telegram_id
        profile.bind_code = None
        profile.save()
        return Response({"status": "ok"})