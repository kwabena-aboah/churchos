import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from .constants import Role


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.SUPER_ADMIN)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=30, choices=Role.CHOICES, default=Role.DATA_ENTRY)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="users/avatars/", null=True, blank=True)

    # Link to a member record (optional — staff may also be church members)
    member = models.OneToOneField(
        "members.Member",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="user_account"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    # Cell group restriction for Cell Leaders
    cell_group = models.ForeignKey(
        "core.CellGroup",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="leaders",
        help_text="For Cell Leader role: restricts view to this group only"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def role_level(self):
        return Role.LEVELS.get(self.role, 0)

    def has_role(self, *roles):
        return self.role in roles

    def is_finance_role(self):
        return self.role in Role.FINANCE_ROLES

    def is_admin_role(self):
        return self.role in Role.ADMIN_ROLES


class UserActivityLog(models.Model):
    """Track significant user actions for the audit trail."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} — {self.action} at {self.timestamp}"
