from rest_framework import serializers
from .models import Department, Worker, SalaryAllowance, SalaryDeduction, PayrollRun, Payslip, LeaveRequest


class DepartmentSerializer(serializers.ModelSerializer):
    worker_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = "__all__"

    def get_worker_count(self, obj):
        return obj.workers.filter(is_active=True, employment_status="active").count()


class SalaryAllowanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryAllowance
        fields = "__all__"


class SalaryDeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryDeduction
        fields = "__all__"


class WorkerListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = [
            "id", "employee_id", "full_name", "job_title", "department",
            "department_name", "employment_type", "employment_status",
            "basic_salary", "start_date", "phone", "email",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class WorkerDetailSerializer(serializers.ModelSerializer):
    allowances = SalaryAllowanceSerializer(many=True, read_only=True)
    deductions = SalaryDeductionSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = "__all__"

    def get_full_name(self, obj):
        return obj.get_full_name()


class PayrollRunSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)

    class Meta:
        model = PayrollRun
        fields = "__all__"
        read_only_fields = ["total_gross", "total_deductions", "total_net", "approved_by", "approved_at"]


class PayslipSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source="worker.get_full_name", read_only=True)
    worker_job_title = serializers.CharField(source="worker.job_title", read_only=True)
    payroll_label = serializers.CharField(source="payroll_run.__str__", read_only=True)

    class Meta:
        model = Payslip
        fields = "__all__"


class LeaveRequestSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source="worker.get_full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = "__all__"
        read_only_fields = ["approved_by", "approved_at"]
