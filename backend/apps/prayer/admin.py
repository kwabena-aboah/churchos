from django.contrib import admin
from .models import PrayerRequest, PrayerUpdate

class PrayerUpdateInline(admin.TabularInline):
    model = PrayerUpdate
    extra = 0
    readonly_fields = ["updated_by", "created_at"]

@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ["title", "member", "status", "privacy", "prayer_count", "assigned_to", "created_at"]
    list_filter = ["status", "privacy"]
    search_fields = ["title", "request_text"]
    inlines = [PrayerUpdateInline]
