from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import path, include
from django.utils import timezone
from rest_framework.routers import DefaultRouter
from .models import Room, RoomBooking, MaintenanceRequest
from apps.core.permissions import IsAdminOrReadOnly


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class RoomBookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    booked_by_name = serializers.CharField(source="booked_by.get_full_name", read_only=True)

    class Meta:
        model = RoomBooking
        fields = "__all__"
        read_only_fields = ["booked_by", "approved_by"]


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.get_full_name", read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = "__all__"
        read_only_fields = ["reported_by"]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(is_active=True)
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ["room_type", "is_bookable"]


class RoomBookingViewSet(viewsets.ModelViewSet):
    queryset = RoomBooking.objects.all().select_related("room", "booked_by")
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["room", "status"]

    def perform_create(self, serializer):
        serializer.save(booked_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        booking = self.get_object()
        booking.status = "approved"
        booking.approved_by = request.user
        booking.save()
        return Response({"status": "approved"})


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all().select_related("room", "reported_by", "assigned_to")
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "priority", "room"]

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        req = self.get_object()
        req.status = "completed"
        req.completed_at = timezone.now()
        req.actual_cost = request.data.get("actual_cost", req.estimated_cost)
        req.notes = request.data.get("notes", req.notes)
        req.save()
        return Response({"status": "completed"})


router = DefaultRouter()
router.register("rooms", RoomViewSet, basename="room")
router.register("bookings", RoomBookingViewSet, basename="room-booking")
router.register("maintenance", MaintenanceRequestViewSet, basename="maintenance")

urlpatterns = [path("", include(router.urls))]
