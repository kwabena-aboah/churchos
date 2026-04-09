from django.db import models
from apps.core.models import BaseModel


class MessageChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    WHATSAPP = "whatsapp", "WhatsApp"


class MessageStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    BOUNCED = "bounced", "Bounced"


class MessageTemplate(BaseModel):
    name = models.CharField(max_length=200)
    channel = models.CharField(max_length=20, choices=MessageChannel.choices)
    event_type = models.CharField(max_length=100, blank=True, help_text="e.g. BIRTHDAY, WELCOME, RECEIPT")
    subject = models.CharField(max_length=300, blank=True, help_text="Email subject line")
    body = models.TextField(help_text="Use {{first_name}}, {{amount}}, {{date}}, {{church_name}} etc.")
    is_html = models.BooleanField(default=False, help_text="For email: use HTML body")
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ["channel", "event_type", "is_default"]
        ordering = ["channel", "name"]

    def __str__(self):
        return f"[{self.channel}] {self.name}"


class MessageLog(BaseModel):
    member = models.ForeignKey(
        "members.Member", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="message_logs"
    )
    channel = models.CharField(max_length=20, choices=MessageChannel.choices)
    recipient = models.CharField(max_length=200, help_text="Phone/email/WhatsApp number")
    subject = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=MessageStatus.choices, default=MessageStatus.PENDING)
    event_type = models.CharField(max_length=100, blank=True)
    provider_reference = models.CharField(max_length=300, blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="sent_messages"
    )
    cost_units = models.PositiveIntegerField(default=1, help_text="SMS credit units used")

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["channel", "status"])]

    def __str__(self):
        return f"[{self.channel}] → {self.recipient} ({self.status})"


class Broadcast(BaseModel):
    """A bulk message sent to a group of members."""
    title = models.CharField(max_length=200)
    template = models.ForeignKey(MessageTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    channels = models.JSONField(default=list, help_text='["email", "sms"]')
    subject = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    target_group = models.CharField(
        max_length=50,
        choices=[
            ("all_active", "All Active Members"),
            ("cell_group", "Specific Cell Group"),
            ("zone", "Specific Zone"),
            ("visitors", "Visitors"),
            ("custom", "Custom Filter"),
        ],
        default="all_active"
    )
    target_cell_group = models.ForeignKey(
        "core.CellGroup", on_delete=models.SET_NULL, null=True, blank=True
    )
    target_zone = models.ForeignKey("core.Zone", on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("draft", "Draft"), ("scheduled", "Scheduled"), ("sent", "Sent"), ("failed", "Failed")],
        default="draft"
    )
    recipient_count = models.PositiveIntegerField(default=0)
    sent_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
