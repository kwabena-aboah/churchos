from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .models import AuditCheck, AuditReport
from apps.core.permissions import IsAdminOrAbove
import logging

logger = logging.getLogger(__name__)


class AuditCheckSerializer(serializers.ModelSerializer):
    last_run = serializers.SerializerMethodField()
    last_status = serializers.SerializerMethodField()

    class Meta:
        model = AuditCheck
        fields = "__all__"

    def get_last_run(self, obj):
        last = obj.reports.first()
        return last.run_at if last else None

    def get_last_status(self, obj):
        last = obj.reports.first()
        return last.status if last else None


class AuditReportSerializer(serializers.ModelSerializer):
    check_name = serializers.CharField(source="audit_check.name", read_only=True)
    check_category = serializers.CharField(source="audit_check.category", read_only=True)
    check_severity = serializers.CharField(source="audit_check.severity", read_only=True)
    resolved_by_name = serializers.CharField(source="resolved_by.get_full_name", read_only=True)

    class Meta:
        model = AuditReport
        fields = "__all__"


def run_check_unreceipted_transactions():
    """Transactions older than 7 days with no receipt PDF."""
    from apps.finance.models import Transaction
    from django.utils import timezone
    from datetime import timedelta
    cutoff = timezone.now().date() - timedelta(days=7)
    items = Transaction.objects.filter(
        transaction_date__lte=cutoff, receipt_pdf="", is_active=True
    ).values_list("reference", flat=True)
    count = items.count()
    return {
        "status": "fail" if count > 0 else "pass",
        "summary": f"{count} transactions older than 7 days have no receipt PDF.",
        "detail": {"references": list(items[:20])},
        "affected_count": count,
    }


def run_check_unverified_transactions():
    """Expenses over threshold with no secondary verification."""
    from apps.finance.models import Transaction, TransactionType
    from apps.core.models import ChurchSettings
    threshold = ChurchSettings.load().procurement_approval_threshold_1
    items = Transaction.objects.filter(
        transaction_type=TransactionType.EXPENSE,
        amount__gte=threshold, verified=False, is_active=True
    )
    count = items.count()
    return {
        "status": "fail" if count > 0 else "pass",
        "summary": f"{count} expenses above {threshold} are unverified.",
        "detail": {"ids": [str(t.id) for t in items[:20]]},
        "affected_count": count,
    }


def run_check_members_no_contact():
    """Active members with no phone or email."""
    from apps.members.models import Member, MemberStatus
    items = Member.objects.filter(
        membership_status=MemberStatus.ACTIVE,
        is_active=True
    ).filter(phone_primary="", email="")
    count = items.count()
    return {
        "status": "warning" if count > 0 else "pass",
        "summary": f"{count} active members have no contact information.",
        "detail": {"ids": [str(m.id) for m in items[:20]]},
        "affected_count": count,
    }


def run_check_workers_no_payroll():
    """Active workers with no payslip in last 2 months."""
    from apps.workers.models import Worker, Payslip
    from django.utils import timezone
    workers = Worker.objects.filter(is_active=True, employment_status="active", employment_type__in=["full_time", "part_time"])
    now = timezone.now()
    flagged = []
    for w in workers:
        last = Payslip.objects.filter(worker=w).order_by("-created_at").first()
        if not last:
            flagged.append(str(w.id))
        elif (now - last.created_at).days > 60:
            flagged.append(str(w.id))
    count = len(flagged)
    return {
        "status": "warning" if count > 0 else "pass",
        "summary": f"{count} active workers have no payslip in the last 60 days.",
        "detail": {"ids": flagged[:20]},
        "affected_count": count,
    }


def run_check_open_procurement():
    """Purchase orders open > 30 days."""
    from apps.procurement.models import PurchaseOrder
    from django.utils import timezone
    from datetime import timedelta
    cutoff = timezone.now().date() - timedelta(days=30)
    items = PurchaseOrder.objects.filter(
        status__in=["draft", "sent"], order_date__lte=cutoff
    )
    count = items.count()
    return {
        "status": "warning" if count > 0 else "pass",
        "summary": f"{count} purchase orders have been open for more than 30 days.",
        "detail": {"references": [p.reference for p in items[:20]]},
        "affected_count": count,
    }


def run_check_duplicate_transactions():
    """Same amount + member + date transactions."""
    from apps.finance.models import Transaction
    from django.db.models import Count
    dupes = (
        Transaction.objects
        .values("member", "amount", "transaction_date")
        .annotate(cnt=Count("id"))
        .filter(cnt__gt=1, member__isnull=False)
    )
    count = dupes.count()
    return {
        "status": "warning" if count > 0 else "pass",
        "summary": f"{count} potential duplicate transactions detected.",
        "detail": {"groups": list(dupes[:10])},
        "affected_count": count,
    }


CHECK_FUNCTIONS = {
    "run_check_unreceipted_transactions": run_check_unreceipted_transactions,
    "run_check_unverified_transactions": run_check_unverified_transactions,
    "run_check_members_no_contact": run_check_members_no_contact,
    "run_check_workers_no_payroll": run_check_workers_no_payroll,
    "run_check_open_procurement": run_check_open_procurement,
    "run_check_duplicate_transactions": run_check_duplicate_transactions,
}


def run_single_check(audit_check: AuditCheck) -> AuditReport:
    func = CHECK_FUNCTIONS.get(audit_check.check_function)
    if not func:
        return None
    result = func()
    report = AuditReport.objects.create(
        audit_check=audit_check,
        status=result["status"],
        result_summary=result["summary"],
        result_detail=result["detail"],
        affected_count=result["affected_count"],
    )
    return report


class AuditCheckViewSet(viewsets.ModelViewSet):
    queryset = AuditCheck.objects.filter(is_active=True)
    serializer_class = AuditCheckSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAbove]

    @action(detail=True, methods=["post"], url_path="run")
    def run(self, request, pk=None):
        audit_check = self.get_object()
        report = run_single_check(audit_check)
        if not report:
            return Response({"error": "Check function not found."}, status=400)
        return Response(AuditReportSerializer(report).data)

    @action(detail=False, methods=["post"], url_path="run-all")
    def run_all(self, request):
        checks = AuditCheck.objects.filter(is_active=True, is_enabled=True)
        results = []
        for audit_check in checks:
            try:
                report = run_single_check(audit_check)
                if report:
                    results.append({"audit_check": audit_check.name, "status": report.status, "affected": report.affected_count})
            except Exception as e:
                logger.error(f"Audit audit_check {audit_check.name} failed: {e}")
        return Response({"results": results, "total": len(results)})

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        from django.db.models import Count
        checks = AuditCheck.objects.filter(is_active=True)
        latest_reports = []
        for audit_check in checks:
            last = audit_check.reports.first()
            if last:
                latest_reports.append({
                    "audit_check": audit_check.name,
                    "category": audit_check.category,
                    "severity": audit_check.severity,
                    "status": last.status,
                    "summary": last.result_summary,
                    "affected_count": last.affected_count,
                    "run_at": last.run_at,
                    "resolved": last.resolved,
                })
        summary = {
            "pass": sum(1 for r in latest_reports if r["status"] == "pass"),
            "warning": sum(1 for r in latest_reports if r["status"] == "warning"),
            "fail": sum(1 for r in latest_reports if r["status"] == "fail"),
        }
        return Response({"summary": summary, "checks": latest_reports})


class AuditReportViewSet(viewsets.ModelViewSet):
    queryset = AuditReport.objects.all().select_related("audit_check", "resolved_by")
    serializer_class = AuditReportSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAbove]
    filterset_fields = ["audit_check", "status", "resolved"]

    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request, pk=None):
        from django.utils import timezone
        report = self.get_object()
        report.resolved = True
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.save()
        return Response({"status": "resolved"})


router = DefaultRouter()
router.register("checks", AuditCheckViewSet, basename="audit-check")
router.register("reports", AuditReportViewSet, basename="audit-report")

urlpatterns = [path("", include(router.urls))]
