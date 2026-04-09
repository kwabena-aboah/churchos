from django.db import models
from apps.core.models import BaseModel


class EventType(models.TextChoices):
    SERVICE = "service", "Church Service"
    CONFERENCE = "conference", "Conference"
    OUTREACH = "outreach", "Outreach"
    MEETING = "meeting", "Meeting"
    CONCERT = "concert", "Concert / Program"
    TRAINING = "training", "Training"
    PRAYER = "prayer", "Prayer Meeting"
    OTHER = "other", "Other"


class Event(BaseModel):
    title = models.CharField(max_length=300)
    event_type = models.CharField(max_length=30, choices=EventType.choices, default=EventType.SERVICE)
    description = models.TextField(blank=True)
    flyer = models.ImageField(upload_to="events/flyers/", null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=100, blank=True, help_text="RRULE string")
    venue_name = models.CharField(max_length=300, blank=True)
    venue_address = models.TextField(blank=True)
    is_online = models.BooleanField(default=False)
    online_link = models.URLField(blank=True)
    is_paid = models.BooleanField(default=False)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    requires_registration = models.BooleanField(default=False)
    organizer = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    send_reminders = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_datetime"]
        indexes = [models.Index(fields=["start_datetime"])]

    def __str__(self):
        return self.title

    @property
    def registered_count(self):
        return self.registrations.filter(status="confirmed").count()

    @property
    def is_full(self):
        if not self.capacity:
            return False
        return self.registered_count >= self.capacity


class EventRegistration(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, null=True, blank=True, related_name="event_registrations")
    guest_name = models.CharField(max_length=200, blank=True, help_text="For non-member guests")
    guest_phone = models.CharField(max_length=20, blank=True)
    guest_email = models.EmailField(blank=True)
    ticket_ref = models.CharField(max_length=50, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=[("confirmed", "Confirmed"), ("waitlist", "Waitlisted"), ("cancelled", "Cancelled")], default="confirmed")
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[("paid", "Paid"), ("free", "Free"), ("pending", "Pending")], default="free")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = [["event", "member"]]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.ticket_ref:
            import uuid
            self.ticket_ref = f"TKT-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class EventAttendance(BaseModel):
    """Manual attendance entry (for services without pre-registration)."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendance_records", null=True, blank=True)
    service_type = models.ForeignKey("core.ServiceType", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    member = models.ForeignKey("members.Member", on_delete=models.SET_NULL, null=True, blank=True)
    is_visitor = models.BooleanField(default=False)
    visitor_name = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = [["date", "member", "service_type"]]
        ordering = ["-date"]
