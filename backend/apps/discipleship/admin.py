from django.contrib import admin
from .models import DiscipleshipTrack, DiscipleshipClass, DiscipleshipEnrollment

@admin.register(DiscipleshipTrack)
class DiscipleshipTrackAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "duration_weeks"]
    ordering = ["order"]

@admin.register(DiscipleshipClass)
class DiscipleshipClassAdmin(admin.ModelAdmin):
    list_display = ["name", "track", "facilitator", "start_date", "end_date"]
    list_filter = ["track"]

@admin.register(DiscipleshipEnrollment)
class DiscipleshipEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["member", "discipleship_class", "status", "enrolled_at", "completed_at", "certificate_issued"]
    list_filter = ["status", "discipleship_class", "certificate_issued"]
