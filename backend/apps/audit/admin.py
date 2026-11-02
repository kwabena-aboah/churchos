from django.contrib import admin
from .models import AuditCheck, AuditReport

@admin.register(AuditCheck)
class AuditCheckAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "severity", "run_schedule", "is_enabled"]
    list_filter = ["category", "severity", "is_enabled", "run_schedule"]
    search_fields = ["name"]

@admin.register(AuditReport)
class AuditReportAdmin(admin.ModelAdmin):
    list_display = ["audit_check", "status", "affected_count", "run_at", "resolved"]
    list_filter = ["status", "resolved", "audit_check__category"]
    readonly_fields = ["audit_check", "status", "result_summary", "result_detail", "affected_count", "run_at"]
    ordering = ["-run_at"]
