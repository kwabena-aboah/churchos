from django.contrib import admin
from .models import Event, EventRegistration, EventAttendance

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_type", "start_datetime", "venue_name", "is_paid", "requires_registration"]
    list_filter = ["event_type", "is_paid", "requires_registration"]
    search_fields = ["title", "venue_name"]
    ordering = ["-start_datetime"]

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ["event", "member", "guest_name", "ticket_ref", "status", "checked_in"]
    list_filter = ["status", "checked_in", "payment_status"]
    search_fields = ["ticket_ref", "guest_name", "member__first_name", "member__last_name"]

@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ["date", "member", "service_type", "is_visitor"]
    list_filter = ["service_type", "date"]
    ordering = ["-date"]
