from django.db import models
from apps.core.models import BaseModel


class FollowUpCase(BaseModel):
    CASE_TYPES = [
        ("absentee", "Absentee"), ("new_visitor", "New Visitor"),
        ("bereavement", "Bereavement"), ("illness", "Illness"),
        ("spiritual_crisis", "Spiritual Crisis"), ("other", "Other"),
    ]
    PRIORITIES = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")]
    STATUSES = [("open", "Open"), ("in_progress", "In Progress"), ("closed", "Closed"), ("escalated", "Escalated")]

    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, related_name="followup_cases")
    case_type = models.CharField(max_length=30, choices=CASE_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITIES, default="medium")
    status = models.CharField(max_length=20, choices=STATUSES, default="open")
    description = models.TextField()
    assigned_to = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_cases")
    target_date = models.DateField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_notes = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="created_cases")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.member.get_full_name()} — {self.case_type}"


class FollowUpLog(BaseModel):
    CONTACT_METHODS = [("call", "Phone Call"), ("visit", "Visit"), ("message", "Message"), ("email", "Email"), ("whatsapp", "WhatsApp")]

    case = models.ForeignKey(FollowUpCase, on_delete=models.CASCADE, related_name="logs")
    contact_method = models.CharField(max_length=20, choices=CONTACT_METHODS)
    contact_date = models.DateField()
    outcome = models.TextField()
    next_action = models.TextField(blank=True)
    next_action_date = models.DateField(null=True, blank=True)
    logged_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-contact_date"]
