from django.db import models
from apps.core.models import BaseModel


class PrayerRequest(BaseModel):
    PRIVACY = [("public", "Public"), ("leaders_only", "Leaders Only"), ("private", "Private")]
    STATUSES = [("open", "Open"), ("praying", "Being Prayed For"), ("answered", "Answered"), ("closed", "Closed")]

    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, null=True, blank=True, related_name="prayer_requests")
    submitter_name = models.CharField(max_length=200, blank=True, help_text="For anonymous/guest submissions")
    title = models.CharField(max_length=300)
    request_text = models.TextField()
    privacy = models.CharField(max_length=20, choices=PRIVACY, default="leaders_only")
    status = models.CharField(max_length=20, choices=STATUSES, default="open")
    assigned_to = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_prayers")
    testimony = models.TextField(blank=True, help_text="Answered prayer testimony")
    answered_at = models.DateField(null=True, blank=True)
    prayer_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PrayerUpdate(BaseModel):
    prayer_request = models.ForeignKey(PrayerRequest, on_delete=models.CASCADE, related_name="updates")
    update_text = models.TextField()
    updated_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-created_at"]
