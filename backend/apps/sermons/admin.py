from django.contrib import admin
from .models import Speaker, SermonSeries, Sermon

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ["name", "title", "is_external"]
    search_fields = ["name"]

@admin.register(SermonSeries)
class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ["title", "start_date", "end_date", "is_complete", "sermon_count"]
    list_filter = ["is_complete"]

@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ["title", "date", "speaker", "series", "primary_scripture", "is_public"]
    list_filter = ["series", "speaker", "service_type", "is_public"]
    search_fields = ["title", "primary_scripture", "transcript"]
    ordering = ["-date"]
    readonly_fields = ["transcript_generated_at", "ai_summary", "ai_key_points", "ai_scriptures_extracted"]
