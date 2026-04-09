from django.contrib import admin
from .models import MessageTemplate, MessageLog, Broadcast

@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "event_type", "is_default"]
    list_filter = ["channel", "event_type"]

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ["recipient", "channel", "event_type", "status", "sent_at", "created_at"]
    list_filter = ["channel", "status", "event_type"]
    search_fields = ["recipient", "subject"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "target_group", "recipient_count", "sent_at"]
    list_filter = ["status", "target_group"]
