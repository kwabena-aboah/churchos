from django.db import models
from auditlog.registry import auditlog
from apps.core.models import BaseModel


class Vendor(BaseModel):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    category = models.CharField(max_length=150, blank=True, help_text="Electronics, Stationery, etc.")
    tax_id = models.CharField(max_length=50, blank=True)
    rating = models.PositiveSmallIntegerField(default=3, help_text="1-5 star rating")
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class PurchaseRequest(BaseModel):
    STATUS_CHOICES = [
        ("draft", "Draft"), ("pending", "Pending Approval"),
        ("approved", "Approved"), ("rejected", "Rejected"), ("ordered", "Ordered"),
    ]

    reference = models.CharField(max_length=30, unique=True, blank=True)
    title = models.CharField(max_length=300)
    department = models.CharField(max_length=150, blank=True)
    requested_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="purchase_requests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    total_estimated = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    justification = models.TextField()
    date_needed = models.DateField(null=True, blank=True)

    # Approval
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_requests")
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            count = PurchaseRequest.objects.count() + 1
            from django.utils import timezone
            self.reference = f"PR-{timezone.now().year}-{str(count).zfill(4)}"
        super().save(*args, **kwargs)


class PurchaseRequestItem(models.Model):
    request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=50, blank=True)
    estimated_unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=300, blank=True)

    @property
    def total_price(self):
        return self.quantity * self.estimated_unit_price


class PurchaseOrder(BaseModel):
    STATUS_CHOICES = [
        ("draft", "Draft"), ("sent", "Sent to Vendor"),
        ("partial", "Partially Received"), ("received", "Fully Received"), ("cancelled", "Cancelled"),
    ]

    reference = models.CharField(max_length=30, unique=True, blank=True)
    purchase_request = models.OneToOneField(PurchaseRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="purchase_order")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    order_date = models.DateField()
    expected_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-order_date"]

    def __str__(self):
        return f"{self.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            count = PurchaseOrder.objects.count() + 1
            self.reference = f"PO-{self.order_date.year}-{str(count).zfill(4)}"
        super().save(*args, **kwargs)


auditlog.register(PurchaseRequest)
auditlog.register(PurchaseOrder)
