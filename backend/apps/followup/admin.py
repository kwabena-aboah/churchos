from django.contrib import admin
from .models import FollowUpCase, FollowUpLog

class FollowUpLogInline(admin.TabularInline):
    model = FollowUpLog
    extra = 0
    readonly_fields = ["logged_by", "created_at"]

@admin.register(FollowUpCase)
class FollowUpCaseAdmin(admin.ModelAdmin):
    list_display = ["member", "case_type", "priority", "status", "assigned_to", "target_date", "created_at"]
    list_filter = ["case_type", "priority", "status"]
    search_fields = ["member__first_name", "member__last_name", "description"]
    inlines = [FollowUpLogInline]
