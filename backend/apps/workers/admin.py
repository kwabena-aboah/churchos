from django.contrib import admin
from .models import Department, Worker, SalaryAllowance, SalaryDeduction, PayrollRun, Payslip, LeaveRequest

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "head"]
    search_fields = ["name"]

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "get_full_name", "job_title", "department", "employment_type", "employment_status", "basic_salary"]
    list_filter = ["department", "employment_type", "employment_status"]
    search_fields = ["first_name", "last_name", "employee_id", "job_title"]
    readonly_fields = ["employee_id"]

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ["__str__", "status", "total_gross", "total_deductions", "total_net", "approved_by"]
    list_filter = ["status", "year"]

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ["worker", "payroll_run", "gross_salary", "net_salary", "payment_status"]
    list_filter = ["payment_status", "payroll_run"]

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ["worker", "leave_type", "start_date", "end_date", "days_requested", "status"]
    list_filter = ["leave_type", "status"]
