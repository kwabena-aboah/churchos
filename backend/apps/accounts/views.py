from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    UserCreateSerializer, ChangePasswordSerializer, UserProfileSerializer,
)
from apps.core.permissions import IsAdminOrAbove, IsSuperAdmin
from .models import UserActivityLog

User = get_user_model()


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Log login
            user_data = response.data.get("user", {})
            ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
            try:
                user = User.objects.get(email=request.data.get("email"))
                user.last_login_ip = ip
                user.save(update_fields=["last_login_ip"])
                UserActivityLog.objects.create(
                    user=user, action="LOGIN",
                    description="User logged in",
                    ip_address=ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
                )
            except User.DoesNotExist:
                pass
        return response


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            UserActivityLog.objects.create(
                user=request.user, action="LOGOUT",
                description="User logged out",
            )
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    """Current user profile."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserProfileSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        UserActivityLog.objects.create(
            user=user, action="PASSWORD_CHANGE",
            description="User changed their password",
        )
        return Response({"message": "Password updated successfully."})


class UserViewSet(viewsets.ModelViewSet):
    """Admin: manage all system users."""
    queryset = User.objects.all().order_by("first_name")
    permission_classes = [IsAuthenticated, IsAdminOrAbove]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsSuperAdmin])
    def activity_logs(self, request):
        from rest_framework.pagination import PageNumberPagination
        logs = UserActivityLog.objects.select_related("user").order_by("-timestamp")
        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(logs, request)
        data = [
            {
                "id": str(log.id),
                "user": log.user.get_full_name(),
                "action": log.action,
                "description": log.description,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp,
            }
            for log in page
        ]
        return paginator.get_paginated_response(data)
