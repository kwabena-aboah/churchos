from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Event, EventRegistration, EventAttendance
from .serializers import EventListSerializer, EventDetailSerializer, EventRegistrationSerializer, EventAttendanceSerializer
from apps.core.permissions import IsAdminOrReadOnly


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["title", "venue_name"]
    filterset_fields = ["event_type", "is_paid"]
    ordering_fields = ["start_datetime", "title"]

    def get_serializer_class(self):
        if self.action == "list":
            return EventListSerializer
        return EventDetailSerializer

    @action(detail=False, methods=["get"], url_path="upcoming")
    def upcoming(self, request):
        events = self.get_queryset().filter(start_datetime__gte=timezone.now()).order_by("start_datetime")[:10]
        serializer = EventListSerializer(events, many=True, context={"request": request})
        return Response(serializer.data)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all().select_related("event", "member")
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["event", "status", "payment_status"]

    @action(detail=True, methods=["post"], url_path="checkin")
    def checkin(self, request, pk=None):
        reg = self.get_object()
        reg.checked_in = True
        reg.checked_in_at = timezone.now()
        reg.save()
        return Response({"status": "checked_in", "name": reg.member.get_full_name() if reg.member else reg.guest_name})

    @action(detail=False, methods=["post"], url_path="checkin-by-ticket")
    def checkin_by_ticket(self, request):
        ticket_ref = request.data.get("ticket_ref", "").upper()
        try:
            reg = EventRegistration.objects.get(ticket_ref=ticket_ref)
            reg.checked_in = True
            reg.checked_in_at = timezone.now()
            reg.save()
            return Response({
                "status": "checked_in",
                "name": reg.member.get_full_name() if reg.member else reg.guest_name,
                "event": reg.event.title,
            })
        except EventRegistration.DoesNotExist:
            return Response({"error": "Invalid ticket reference."}, status=404)


class EventAttendanceViewSet(viewsets.ModelViewSet):
    queryset = EventAttendance.objects.all().select_related("event", "member", "service_type")
    serializer_class = EventAttendanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["date", "service_type", "event"]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
