import uuid
from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog
from apps.core.models import BaseModel, Zone, CellGroup


class MemberStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    VISITOR = "visitor", "Visitor"
    TRANSFERRED_OUT = "transferred_out", "Transferred Out"
    TRANSFERRED_IN = "transferred_in", "Transferred In"
    DECEASED = "deceased", "Deceased"
    EXCOMMUNICATED = "excommunicated", "Excommunicated"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


class MaritalStatus(models.TextChoices):
    SINGLE = "single", "Single"
    MARRIED = "married", "Married"
    WIDOWED = "widowed", "Widowed"
    DIVORCED = "divorced", "Divorced"
    SEPARATED = "separated", "Separated"


class Member(BaseModel):
    # ── Identity ──────────────────────────────────────────────────────────────
    member_number = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    preferred_name = models.CharField(max_length=100, blank=True, help_text="Name they go by")
    gender = models.CharField(max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MaritalStatus.choices, blank=True)
    photo = models.ImageField(upload_to="members/photos/", null=True, blank=True)
    national_id = models.CharField(max_length=50, blank=True)

    # ── Contact ───────────────────────────────────────────────────────────────
    phone_primary = models.CharField(max_length=20)
    phone_secondary = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Ghana")
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="If different from primary phone")

    # ── Membership ────────────────────────────────────────────────────────────
    membership_status = models.CharField(max_length=20, choices=MemberStatus.choices, default=MemberStatus.VISITOR)
    membership_date = models.DateField(null=True, blank=True, help_text="Date of full membership")
    visitor_date = models.DateField(null=True, blank=True, help_text="Date first visited")
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True, related_name="members")
    cell_group = models.ForeignKey(CellGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="members")

    # ── Spiritual ─────────────────────────────────────────────────────────────
    salvation_date = models.DateField(null=True, blank=True)
    baptism_date = models.DateField(null=True, blank=True)
    baptism_type = models.CharField(max_length=50, blank=True, help_text="Water, Holy Spirit, etc.")
    came_from_church = models.CharField(max_length=200, blank=True, help_text="Previous church if transferred in")
    spiritual_gifts = models.TextField(blank=True)
    ministry_interests = models.TextField(blank=True)

    # ── Professional ──────────────────────────────────────────────────────────
    occupation = models.CharField(max_length=150, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    education_level = models.CharField(max_length=100, blank=True)

    # ── Family ────────────────────────────────────────────────────────────────
    spouse = models.OneToOneField(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="spouse_of"
    )
    children_count = models.PositiveSmallIntegerField(default=0)

    # ── Emergency ─────────────────────────────────────────────────────────────
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)

    # ── Communication Preferences ─────────────────────────────────────────────
    receive_sms = models.BooleanField(default=True)
    receive_email = models.BooleanField(default=True)
    receive_whatsapp = models.BooleanField(default=True)

    # ── Notes ─────────────────────────────────────────────────────────────────
    notes = models.TextField(blank=True, help_text="Internal pastoral notes")

    # ── Status change tracking ────────────────────────────────────────────────
    status_changed_date = models.DateField(null=True, blank=True)
    status_change_reason = models.TextField(blank=True)
    transferred_to_church = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["membership_status"]),
            models.Index(fields=["date_of_birth"]),
            models.Index(fields=["phone_primary"]),
            models.Index(fields=["email"]),
            models.Index(fields=["member_number"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.member_number})"

    def get_full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p).strip()

    def get_display_name(self):
        return self.preferred_name or self.first_name

    def get_whatsapp_number(self):
        return self.whatsapp_number or self.phone_primary

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def is_birthday_today(self):
        if not self.date_of_birth:
            return False
        today = timezone.now().date()
        return self.date_of_birth.month == today.month and self.date_of_birth.day == today.day

    @property
    def years_as_member(self):
        if not self.membership_date:
            return None
        today = timezone.now().date()
        return today.year - self.membership_date.year

    def save(self, *args, **kwargs):
        if not self.member_number:
            self.member_number = self._generate_member_number()
        super().save(*args, **kwargs)

    def _generate_member_number(self):
        from apps.core.models import ChurchSettings
        settings = ChurchSettings.load()
        prefix = settings.member_number_prefix
        padding = settings.member_number_padding
        last = Member.objects.order_by("-created_at").first()
        if last and last.member_number:
            try:
                num = int(last.member_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        return f"{prefix}-{str(num).zfill(padding)}"


class MemberDocument(BaseModel):
    """Attached documents for a member (ID, certificate, etc.)."""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=100)
    file = models.FileField(upload_to="members/documents/")
    description = models.CharField(max_length=300, blank=True)
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.member.get_full_name()} — {self.document_type}"


class MemberStatusHistory(models.Model):
    """Log every status change for a member."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]


# Register models with django-auditlog
auditlog.register(Member)
