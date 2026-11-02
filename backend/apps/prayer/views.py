"""Prayer app views and urls."""
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .models import PrayerRequest, PrayerUpdate
from apps.core.permissions import IsPastorOrAbove


class PrayerUpdateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source="updated_by.get_full_name", read_only=True)

    class Meta:
        model = PrayerUpdate
        fields = "__all__"


class PrayerRequestSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    updates = PrayerUpdateSerializer(many=True, read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)

    class Meta:
        model = PrayerRequest
        fields = "__all__"

    def get_member_name(self, obj):
        return obj.member.get_full_name() if obj.member else obj.submitter_name


class PrayerRequestViewSet(viewsets.ModelViewSet):
    queryset = PrayerRequest.objects.all().select_related("member", "assigned_to")
    serializer_class = PrayerRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "privacy", "assigned_to"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role not in {"super_admin", "administrator", "pastor"}:
            qs = qs.exclude(privacy="private").exclude(privacy="leaders_only")
        return qs

    @action(detail=True, methods=["post"], url_path="add-update")
    def add_update(self, request, pk=None):
        prayer = self.get_object()
        serializer = PrayerUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(prayer_request=prayer, updated_by=request.user)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["post"], url_path="mark-answered")
    def mark_answered(self, request, pk=None):
        prayer = self.get_object()
        prayer.status = "answered"
        prayer.testimony = request.data.get("testimony", "")
        from django.utils import timezone
        prayer.answered_at = timezone.now().date()
        prayer.save()
        return Response({"status": "answered"})

    @action(detail=True, methods=["post"], url_path="pray")
    def pray(self, request, pk=None):
        prayer = self.get_object()
        prayer.prayer_count += 1
        if prayer.status == "open":
            prayer.status = "praying"
        prayer.save(update_fields=["prayer_count", "status"])
        return Response({"prayer_count": prayer.prayer_count})


router = DefaultRouter()
router.register("", PrayerRequestViewSet, basename="prayer-request")

urlpatterns = [path("", include(router.urls))]
