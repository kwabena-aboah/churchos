from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog
from apps.core.models import BaseModel


class BudgetYear(BaseModel):
    year = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_budgets")
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-year"]

    def __str__(self):
        return f"Budget {self.year}"

    @property
    def total_income_budget(self):
        return self.lines.filter(line_type="income").aggregate(t=models.Sum("amount"))["t"] or 0

    @property
    def total_expense_budget(self):
        return self.lines.filter(line_type="expense").aggregate(t=models.Sum("amount"))["t"] or 0


class BudgetCategory(BaseModel):
    name = models.CharField(max_length=150)
    department = models.CharField(max_length=150, blank=True)
    line_type = models.CharField(max_length=10, choices=[("income", "Income"), ("expense", "Expense")])
    description = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Budget Categories"

    def __str__(self):
        return self.name


class BudgetLine(BaseModel):
    budget_year = models.ForeignKey(BudgetYear, on_delete=models.CASCADE, related_name="lines")
    category = models.ForeignKey(BudgetCategory, on_delete=models.PROTECT, related_name="budget_lines")
    line_type = models.CharField(max_length=10, choices=[("income", "Income"), ("expense", "Expense")])
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    q1_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    q2_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    q3_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    q4_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = [("budget_year", "category")]
        ordering = ["category__sort_order"]

    def __str__(self):
        return f"{self.budget_year} — {self.category.name}"

    @property
    def actual_amount(self):
        """Pull actuals from finance transactions."""
        return 0  # Computed in analytics layer


class BudgetAmendment(BaseModel):
    budget_line = models.ForeignKey(BudgetLine, on_delete=models.CASCADE, related_name="amendments")
    old_amount = models.DecimalField(max_digits=14, decimal_places=2)
    new_amount = models.DecimalField(max_digits=14, decimal_places=2)
    reason = models.TextField()
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    approved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Amendment to {self.budget_line}"


auditlog.register(BudgetYear)
auditlog.register(BudgetLine)
