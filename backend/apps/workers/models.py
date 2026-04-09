from django.db import models
from apps.core.models import BaseModel


class Department(BaseModel):
    name = models.CharField(max_length=150)
    head = models.ForeignKey("Worker", on_delete=models.SET_NULL, null=True, blank=True, related_name="headed_departments")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Worker(BaseModel):
    member = models.OneToOneField("members.Member", on_delete=models.SET_NULL, null=True, blank=True, related_name="worker_profile")
    first_name = models.CharField(max_length=100, blank=True, help_text="If not linked to member")
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    employee_id = models.CharField(max_length=30, unique=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="workers")
    job_title = models.CharField(max_length=150)
    employment_type = models.CharField(max_length=20, choices=[("full_time", "Full-Time"), ("part_time", "Part-Time"), ("contract", "Contract"), ("volunteer", "Volunteer")], default="full_time")
    employment_status = models.CharField(max_length=20, choices=[("active", "Active"), ("on_leave", "On Leave"), ("terminated", "Terminated"), ("suspended", "Suspended")], default="active")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bank_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    mobile_money_number = models.CharField(max_length=20, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    tin_number = models.CharField(max_length=50, blank=True)
    ssnit_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        if self.member:
            return self.member.get_full_name()
        return f"{self.first_name} {self.last_name}".strip()

    def get_full_name(self):
        if self.member:
            return self.member.get_full_name()
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if not self.employee_id:
            count = Worker.objects.count() + 1
            self.employee_id = f"EMP-{str(count).zfill(4)}"
        super().save(*args, **kwargs)


class SalaryAllowance(BaseModel):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="allowances")
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_recurring = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}: {self.amount}"


class SalaryDeduction(BaseModel):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="deductions")
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_recurring = models.BooleanField(default=True)
    deduction_type = models.CharField(max_length=30, choices=[("paye", "PAYE Tax"), ("ssnit", "SSNIT"), ("nhil", "NHIL"), ("other", "Other")], default="other")


class PayrollRun(BaseModel):
    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[("draft", "Draft"), ("approved", "Approved"), ("paid", "Paid")], default="draft")
    total_gross = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_payrolls")
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ["month", "year"]
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"Payroll {self.month}/{self.year}"


class Payslip(BaseModel):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="payslips")
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="payslips")
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("paid", "Paid")], default="pending")
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=30, blank=True)
    allowances_detail = models.JSONField(default=list)
    deductions_detail = models.JSONField(default=list)
    pdf = models.FileField(upload_to="payslips/", null=True, blank=True)

    class Meta:
        unique_together = ["payroll_run", "worker"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payslip — {self.worker} ({self.payroll_run})"


class LeaveRequest(BaseModel):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=30, choices=[("annual", "Annual"), ("sick", "Sick"), ("maternity", "Maternity"), ("paternity", "Paternity"), ("unpaid", "Unpaid"), ("compassionate", "Compassionate")], default="annual")
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.PositiveSmallIntegerField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("cancelled", "Cancelled")], default="pending")
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
