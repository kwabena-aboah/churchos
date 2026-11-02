from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework import serializers, viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema

from .models import ChurchSettings, ServiceType, Zone, CellGroup
from .serializers import (
    ChurchSettingsSerializer,
    ChurchSettingsPublicSerializer,
    ServiceTypeSerializer,
    ZoneSerializer,
    CellGroupSerializer,
)
from .permissions import IsAdminOrAbove, IsAdminOrReadOnly
from .ai import AIProviderError, generate_ai_response
import logging

logger = logging.getLogger(__name__)


@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"})


class AIChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=("user", "assistant"))
    content = serializers.CharField(max_length=4000, trim_whitespace=True)


class AIChatRequestSerializer(serializers.Serializer):
    messages = AIChatMessageSerializer(many=True, min_length=1, max_length=10)

    def validate_messages(self, messages):
        if messages[-1]["role"] != "user":
            raise serializers.ValidationError("The last message must be from the user.")
        return messages


class AIChatResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    provider = serializers.ChoiceField(choices=("anthropic", "openai", "built_in"))


class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AIChatRequestSerializer,
        responses=AIChatResponseSerializer,
    )
    def post(self, request):
        serializer = AIChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        church = ChurchSettings.get_cached()
        if not church.enable_ai_features:
            return Response(
                {"detail": "AI features are disabled in system settings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            reply, provider = generate_ai_response(
                church,
                serializer.validated_data["messages"],
            )
        except AIProviderError:
            logger.exception("Configured AI provider request failed")
            return Response(
                {"detail": "The configured AI provider could not process this request."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"reply": reply, "provider": provider})


class ChurchSettingsView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/core/settings/          — Full settings (admin only)
    PATCH /api/v1/core/settings/         — Update settings (super-admin only)
    GET  /api/v1/core/settings/public/   — Public branding info (anyone)
    """

    serializer_class = ChurchSettingsSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAbove]

    def get_object(self):
        return ChurchSettings.load()

    @action(detail=False, methods=["get"], permission_classes=[AllowAny], url_path="public")
    def public(self, request):
        settings_obj = ChurchSettings.get_cached()
        serializer = ChurchSettingsPublicSerializer(settings_obj, context={"request": request})
        return Response(serializer.data)


class ChurchSettingsPublicView(generics.RetrieveAPIView):
    """Public branding endpoint — called by Vue frontend on mount."""

    serializer_class = ChurchSettingsPublicSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return ChurchSettings.get_cached()


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.filter(is_active=True)
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["day_of_week", "start_time", "name"]


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.filter(is_active=True)
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["name"]


class CellGroupViewSet(viewsets.ModelViewSet):
    queryset = CellGroup.objects.filter(is_active=True).select_related("zone")
    serializer_class = CellGroupSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ["zone"]
    search_fields = ["name"]
