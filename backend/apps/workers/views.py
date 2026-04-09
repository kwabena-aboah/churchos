from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Department, Worker, SalaryAllowance, SalaryDeduction, PayrollRun, Payslip, LeaveRequest
from .serializers import (
    DepartmentSerializer, WorkerListSerializer, WorkerDetailSerializer,
    SalaryAllowanceSerializer, SalaryDeductionSerializer,
    PayrollRunSerializer, PayslipSerializer, LeaveRequestSerializer,
)
from apps.core.permissions import IsFinanceOrAbove, IsAdminOrAbove, IsAdminOrReadOnly


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["name"]


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.filter(is_active=True).select_related("department", "member")
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["first_name", "last_name", "employee_id", "job_title"]
    filterset_fields = ["department", "employment_type", "employment_status"]

    def get_serializer_class(self):
        if self.action == "list":
            return WorkerListSerializer
        return WorkerDetailSerializer

    @action(detail=True, methods=["get"], url_path="payslips")
    def payslips(self, request, pk=None):
        worker = self.get_object()
        payslips = Payslip.objects.filter(worker=worker).select_related("payroll_run").order_by("-created_at")
        serializer = PayslipSerializer(payslips, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="leave-requests")
    def leave_requests(self, request, pk=None):
        worker = self.get_object()
        leaves = LeaveRequest.objects.filter(worker=worker).order_by("-created_at")
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response(serializer.data)


class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [IsAuthenticated, IsFinanceOrAbove]
    filterset_fields = ["month", "year", "status"]

    @action(detail=True, methods=["post"], url_path="generate")
    def generate(self, request, pk=None):
        """Auto-generate payslips for all active workers."""
        run = self.get_object()
        if run.status != "draft":
            return Response({"error": "Can only generate for draft payroll runs."}, status=400)

        workers = Worker.objects.filter(is_active=True, employment_status="active").prefetch_related("allowances", "deductions")
        payslips = []
        total_gross = Decimal("0")
        total_deductions = Decimal("0")
        total_net = Decimal("0")

        for worker in workers:
            allowances = list(worker.allowances.filter(is_active=True, is_recurring=True))
            deductions = list(worker.deductions.filter(is_active=True, is_recurring=True))

            total_allowances = sum(a.amount for a in allowances)
            gross = worker.basic_salary + total_allowances

            calc_deductions = Decimal("0")
            deductions_detail = []
            for d in deductions:
                amount = d.amount if d.amount else (gross * d.percentage / 100)
                calc_deductions += amount
                deductions_detail.append({"name": d.name, "amount": float(amount), "type": d.deduction_type})

            net = gross - calc_deductions

            payslip, created = Payslip.objects.get_or_create(
                payroll_run=run,
                worker=worker,
                defaults={
                    "basic_salary": worker.basic_salary,
                    "total_allowances": total_allowances,
                    "gross_salary": gross,
                    "total_deductions": calc_deductions,
                    "net_salary": net,
                    "allowances_detail": [{"name": a.name, "amount": float(a.amount)} for a in allowances],
                    "deductions_detail": deductions_detail,
                }
            )
            if created:
                payslips.append(payslip)
                total_gross += gross
                total_deductions += calc_deductions
                total_net += net

        run.total_gross = total_gross
        run.total_deductions = total_deductions
        run.total_net = total_net
        run.save()

        return Response({
            "message": f"Generated {len(payslips)} payslips.",
            "total_gross": float(total_gross),
            "total_net": float(total_net),
        })

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        run = self.get_object()
        run.status = "approved"
        run.approved_by = request.user
        run.approved_at = timezone.now()
        run.save()
        return Response({"status": "approved"})


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.all().select_related("worker", "payroll_run")
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated, IsFinanceOrAbove]
    filterset_fields = ["payroll_run", "worker", "payment_status"]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().select_related("worker", "approved_by")
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ["worker", "leave_type", "status"]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = "approved"
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.save()
        return Response({"status": "approved"})

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = "rejected"
        leave.rejection_reason = request.data.get("reason", "")
        leave.approved_by = request.user
        leave.save()
        return Response({"status": "rejected"})
