from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import ChurchSettings, ServiceType, Zone, CellGroup
from .serializers import (
    ChurchSettingsSerializer,
    ChurchSettingsPublicSerializer,
    ServiceTypeSerializer,
    ZoneSerializer,
    CellGroupSerializer,
)
from .permissions import IsAdminOrReadOnly, IsSuperAdmin


class ChurchSettingsView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/core/settings/          — Full settings (admin only)
    PATCH /api/v1/core/settings/         — Update settings (super-admin only)
    GET  /api/v1/core/settings/public/   — Public branding info (anyone)
    """

    serializer_class = ChurchSettingsSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

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
