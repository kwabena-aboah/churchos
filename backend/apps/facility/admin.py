from django.contrib import admin
from .models import Room, RoomBooking, MaintenanceRequest

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["name", "room_type", "capacity", "is_bookable", "floor_number"]
    list_filter = ["room_type", "is_bookable"]

@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ["room", "title", "booked_by", "start_datetime", "end_datetime", "status"]
    list_filter = ["status", "room"]
    ordering = ["-start_datetime"]

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ["title", "room", "priority", "status", "reported_by", "assigned_to", "created_at"]
    list_filter = ["priority", "status"]
