from django.db import models
from auditlog.registry import auditlog
from apps.core.models import BaseModel


class ItemCategory(BaseModel):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Item Categories"

    def __str__(self):
        return self.name


class InventoryItem(BaseModel):
    CONDITION_CHOICES = [
        ("new", "New"), ("good", "Good"), ("fair", "Fair"),
        ("poor", "Poor"), ("written_off", "Written Off"),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="inventory/items/", null=True, blank=True)

    # Location & custody
    location = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=150, blank=True)
    custodian = models.ForeignKey("workers.Worker", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_items")

    # Value
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    useful_life_years = models.PositiveSmallIntegerField(null=True, blank=True)

    # Status
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="good")
    quantity = models.PositiveIntegerField(default=1)
    is_consumable = models.BooleanField(default=False)

    # Procurement link
    from_procurement = models.ForeignKey("procurement.PurchaseOrder", on_delete=models.SET_NULL, null=True, blank=True, related_name="inventory_items")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.condition})"

    @property
    def depreciated_value(self):
        if not self.purchase_price or not self.useful_life_years or not self.purchase_date:
            return self.current_value
        from django.utils import timezone
        years_old = (timezone.now().date() - self.purchase_date).days / 365
        annual_depreciation = float(self.purchase_price) / self.useful_life_years
        depreciated = float(self.purchase_price) - (annual_depreciation * years_old)
        return max(0, round(depreciated, 2))


class ItemMovement(BaseModel):
    MOVEMENT_TYPES = [
        ("transfer", "Transfer"), ("maintenance", "Maintenance"),
        ("disposal", "Disposal"), ("write_off", "Write Off"),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    from_location = models.CharField(max_length=200, blank=True)
    to_location = models.CharField(max_length=200, blank=True)
    reason = models.TextField()
    performed_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.item.name} — {self.movement_type} on {self.date}"


auditlog.register(InventoryItem)
