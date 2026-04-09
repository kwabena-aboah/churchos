import uuid
from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError


class SingletonModel(models.Model):
    """Ensures only one instance of this model can exist."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        self._invalidate_cache()

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion of singleton

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def _invalidate_cache(self):
        cache.delete(f"singleton_{self.__class__.__name__}")


class BaseModel(models.Model):
    """Abstract base model for all ChurchOS models."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def soft_delete(self):
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])


class ChurchSettings(SingletonModel):
    """
    Singleton model that stores all global church configuration.
    Loaded once at startup and cached in Redis.
    """

    # ── Church Identity ─────────────────────────────────────────────────────
    church_name = models.CharField(max_length=200, default="My Church")
    church_tagline = models.CharField(max_length=300, blank=True)
    church_denomination = models.CharField(max_length=150, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)

    # ── Contact ─────────────────────────────────────────────────────────────
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Ghana")
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    po_box = models.CharField(max_length=100, blank=True)

    # ── Branding ─────────────────────────────────────────────────────────────
    logo = models.ImageField(upload_to="church/logo/", null=True, blank=True)
    favicon = models.ImageField(upload_to="church/favicon/", null=True, blank=True)
    primary_color = models.CharField(max_length=7, default="#1a6b3c")   # hex
    secondary_color = models.CharField(max_length=7, default="#2c2c2c")
    accent_color = models.CharField(max_length=7, default="#c9a84c")

    # ── Locale & Finance ─────────────────────────────────────────────────────
    currency_code = models.CharField(max_length=3, default="GHS")
    currency_symbol = models.CharField(max_length=5, default="₵")
    date_format = models.CharField(max_length=30, default="DD/MM/YYYY")
    time_zone = models.CharField(max_length=60, default="Africa/Accra")
    financial_year_start_month = models.PositiveSmallIntegerField(default=1)  # January

    # ── Member Settings ───────────────────────────────────────────────────────
    member_number_prefix = models.CharField(max_length=10, default="CHR")
    member_number_padding = models.PositiveSmallIntegerField(default=4)  # CHR-0001

    # ── Notification Toggles ─────────────────────────────────────────────────
    enable_birthday_email = models.BooleanField(default=True)
    enable_birthday_sms = models.BooleanField(default=True)
    enable_birthday_whatsapp = models.BooleanField(default=False)
    birthday_greeting_hour = models.PositiveSmallIntegerField(default=7)  # 7 AM

    enable_payment_receipt_email = models.BooleanField(default=True)
    enable_payment_receipt_sms = models.BooleanField(default=True)
    enable_event_reminders = models.BooleanField(default=True)

    # ── Integration Keys (encrypted in production via django-fernet-fields) ──
    paystack_public_key = models.CharField(max_length=200, blank=True)
    paystack_secret_key = models.CharField(max_length=200, blank=True)
    twilio_account_sid = models.CharField(max_length=100, blank=True)
    twilio_auth_token = models.CharField(max_length=100, blank=True)
    twilio_sender_id = models.CharField(max_length=20, blank=True)
    sendgrid_api_key = models.CharField(max_length=200, blank=True)
    whatsapp_api_token = models.CharField(max_length=300, blank=True)
    whatsapp_phone_id = models.CharField(max_length=100, blank=True)

    # ── AI ────────────────────────────────────────────────────────────────────
    enable_ai_features = models.BooleanField(default=False)
    ai_weekly_briefing = models.BooleanField(default=False)
    ai_briefing_recipients = models.TextField(
        blank=True,
        help_text="Comma-separated email addresses for weekly AI briefing"
    )

    # ── Security ─────────────────────────────────────────────────────────────
    session_timeout_minutes = models.PositiveIntegerField(default=480)  # 8 hours
    require_2fa_for_finance = models.BooleanField(default=False)
    require_2fa_for_admin = models.BooleanField(default=False)

    # ── Procurement Thresholds ────────────────────────────────────────────────
    procurement_approval_threshold_1 = models.DecimalField(
        max_digits=12, decimal_places=2, default=500,
        help_text="Amount above which single approval is required"
    )
    procurement_approval_threshold_2 = models.DecimalField(
        max_digits=12, decimal_places=2, default=5000,
        help_text="Amount above which double approval is required"
    )

    class Meta:
        verbose_name = "Church Settings"

    def __str__(self):
        return f"{self.church_name} Settings"

    @classmethod
    def get_cached(cls):
        """Load from cache or DB. Use this everywhere in the app."""
        cached = cache.get("singleton_ChurchSettings")
        if cached is None:
            obj = cls.load()
            cache.set("singleton_ChurchSettings", obj, timeout=3600)
            return obj
        return cached

    def get_logo_url(self, request=None):
        if self.logo:
            url = self.logo.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ServiceType(BaseModel):
    """Types of church services: Sunday, Midweek, Special, etc."""

    name = models.CharField(max_length=100)
    day_of_week = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="0=Monday … 6=Sunday"
    )
    start_time = models.TimeField(null=True, blank=True)
    is_recurring = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default="#1a6b3c")

    class Meta:
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return self.name


class Zone(BaseModel):
    """Geographic or departmental zone grouping."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CellGroup(BaseModel):
    """Small group within a zone."""

    name = models.CharField(max_length=150)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True, related_name="cell_groups")
    meeting_day = models.PositiveSmallIntegerField(null=True, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    meeting_location = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.name
