from rest_framework import serializers
from .models import Event, EventRegistration, EventAttendance


class EventListSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "event_type", "start_datetime", "end_datetime",
            "venue_name", "is_paid", "ticket_price", "capacity",
            "registered_count", "is_full", "requires_registration",
            "flyer", "is_active", "created_at",
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class EventRegistrationSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = EventRegistration
        fields = "__all__"
        read_only_fields = ["ticket_ref"]

    def get_member_name(self, obj):
        if obj.member:
            return obj.member.get_full_name()
        return obj.guest_name


class EventAttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()

    class Meta:
        model = EventAttendance
        fields = "__all__"

    def get_member_name(self, obj):
        if obj.member:
            return obj.member.get_full_name()
        return obj.visitor_name
