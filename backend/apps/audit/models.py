from django.db import models
from apps.core.models import BaseModel


class AuditCheck(BaseModel):
    CATEGORIES = [
        ("finance", "Financial"), ("data", "Data Integrity"),
        ("security", "Security"), ("compliance", "Compliance"),
    ]
    SEVERITY = [("info", "Info"), ("warning", "Warning"), ("critical", "Critical")]
    STATUS = [("pass", "Pass"), ("fail", "Fail"), ("warning", "Warning")]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY, default="warning")
    is_enabled = models.BooleanField(default=True)
    check_function = models.CharField(max_length=200, help_text="Dotted path to check function")
    run_schedule = models.CharField(max_length=50, default="daily", choices=[
        ("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"),
    ])

    def __str__(self):
        return self.name


class AuditReport(BaseModel):
    audit_check = models.ForeignKey(AuditCheck, on_delete=models.CASCADE, related_name="reports")
    status = models.CharField(max_length=10, choices=[("pass", "Pass"), ("fail", "Fail"), ("warning", "Warning")])
    result_summary = models.TextField()
    result_detail = models.JSONField(default=dict)
    affected_count = models.PositiveIntegerField(default=0)
    run_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    ai_explanation = models.TextField(blank=True)

    class Meta:
        ordering = ["-run_at"]

    def __str__(self):
        return f"{self.check.name} — {self.status} ({self.run_at.date()})"
