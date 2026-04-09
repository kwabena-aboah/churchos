import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog
from apps.core.models import BaseModel, ServiceType


class TransactionType(models.TextChoices):
    TITHE = "tithe", "Tithe"
    OFFERING = "offering", "Offering"
    DONATION = "donation", "Donation"
    PLEDGE_PAYMENT = "pledge_payment", "Pledge Payment"
    HALL_RENTAL = "hall_rental", "Hall Rental"
    OTHER_INCOME = "other_income", "Other Income"
    EXPENSE = "expense", "Expense"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    MOBILE_MONEY = "mobile_money", "Mobile Money"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CHEQUE = "cheque", "Cheque"
    CARD = "card", "Card (POS)"
    PAYSTACK = "paystack", "Paystack Online"


class FinanceCategory(BaseModel):
    name = models.CharField(max_length=150)
    transaction_type = models.CharField(max_length=30, choices=TransactionType.choices)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False, help_text="System categories cannot be deleted")
    color = models.CharField(max_length=7, default="#1a6b3c")

    class Meta:
        verbose_name_plural = "Finance Categories"
        ordering = ["transaction_type", "name"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} — {self.name}"


class BankAccount(BaseModel):
    name = models.CharField(max_length=200, help_text="e.g. 'Main Offering Account'")
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    branch = models.CharField(max_length=200, blank=True)
    currency = models.CharField(max_length=3, default="GHS")
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_default = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-is_default", "name"]

    def __str__(self):
        return f"{self.name} ({self.bank_name})"


class Cause(BaseModel):
    """A specific fundraising cause/project, e.g. Building Fund."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_ongoing = models.BooleanField(default=False)
    banner = models.ImageField(upload_to="causes/banners/", null=True, blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    @property
    def total_raised(self):
        return self.transactions.filter(
            transaction_type__in=[TransactionType.DONATION, TransactionType.PLEDGE_PAYMENT]
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

    @property
    def progress_percent(self):
        if not self.target_amount or self.target_amount == 0:
            return None
        return min(round((self.total_raised / self.target_amount) * 100, 1), 100)


class Pledge(BaseModel):
    """A member's commitment to give a certain amount (often to a cause)."""
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, related_name="pledges")
    cause = models.ForeignKey(Cause, on_delete=models.SET_NULL, null=True, blank=True, related_name="pledges")
    pledge_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pledge_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_fulfilled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-pledge_date"]

    def __str__(self):
        return f"{self.member} — {self.pledge_amount}"

    @property
    def balance_remaining(self):
        return self.pledge_amount - self.amount_paid

    def update_paid_amount(self):
        from django.db.models import Sum
        paid = self.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        self.amount_paid = paid
        self.is_fulfilled = paid >= self.pledge_amount
        self.save(update_fields=["amount_paid", "is_fulfilled"])


class Transaction(BaseModel):
    reference = models.CharField(max_length=50, unique=True, blank=True)
    member = models.ForeignKey(
        "members.Member", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="transactions",
        help_text="Null = anonymous"
    )
    transaction_type = models.CharField(max_length=30, choices=TransactionType.choices)
    category = models.ForeignKey(
        FinanceCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="transactions"
    )
    cause = models.ForeignKey(
        Cause, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="transactions"
    )
    pledge = models.ForeignKey(
        Pledge, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="GHS")
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    payment_reference = models.CharField(max_length=200, blank=True, help_text="MoMo ref, cheque no, etc.")
    transaction_date = models.DateField(default=timezone.now)
    service = models.ForeignKey(
        ServiceType, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="transactions"
    )
    bank_account = models.ForeignKey(
        BankAccount, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="transactions"
    )
    notes = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=30, blank=True)
    receipt_pdf = models.FileField(upload_to="receipts/", null=True, blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, related_name="recorded_transactions"
    )
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="verified_transactions"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    # Paystack online payment fields
    paystack_reference = models.CharField(max_length=200, blank=True)
    paystack_status = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        indexes = [
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["transaction_date"]),
            models.Index(fields=["member"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.get_transaction_type_display()} {self.amount}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        if not self.receipt_number:
            self.receipt_number = self._generate_receipt_number()
        super().save(*args, **kwargs)
        # Update pledge paid amount if this is a pledge payment
        if self.pledge:
            self.pledge.update_paid_amount()

    def _generate_reference(self):
        date_str = timezone.now().strftime("%Y%m%d")
        count = Transaction.objects.filter(
            created_at__date=timezone.now().date()
        ).count() + 1
        return f"TRX-{date_str}-{str(count).zfill(4)}"

    def _generate_receipt_number(self):
        year = timezone.now().year
        count = Transaction.objects.filter(transaction_date__year=year).count() + 1
        return f"RCP-{year}-{str(count).zfill(5)}"


class ExpenseApproval(BaseModel):
    """Approval chain for high-value expenses."""
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="approval")
    required_approvals = models.PositiveSmallIntegerField(default=1)
    approval_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending"
    )
    approver_1 = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="first_approvals"
    )
    approved_1_at = models.DateTimeField(null=True, blank=True)
    approver_2 = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="second_approvals"
    )
    approved_2_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)


auditlog.register(Transaction)
auditlog.register(Pledge)
