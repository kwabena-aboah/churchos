from decimal import Decimal
import datetime
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import FileResponse, HttpResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from .models import Transaction, FinanceCategory, BankAccount, Cause, Pledge, TransactionType
from .serializers import (
    TransactionListSerializer, TransactionDetailSerializer,
    FinanceCategorySerializer, BankAccountSerializer,
    CauseSerializer, PledgeSerializer,
)
from apps.core.permissions import IsFinanceOrAbove, IsAdminOrReadOnly


class TransactionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="transaction_date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="transaction_date", lookup_expr="lte")
    transaction_type = django_filters.CharFilter(field_name="transaction_type")
    type = django_filters.CharFilter(field_name="transaction_type")
    payment_method = django_filters.CharFilter(field_name="payment_method")
    verified = django_filters.BooleanFilter(field_name="verified")
    member = django_filters.UUIDFilter(field_name="member__id")
    cause = django_filters.UUIDFilter(field_name="cause__id")
    year = django_filters.NumberFilter(field_name="transaction_date__year")
    month = django_filters.NumberFilter(field_name="transaction_date__month")

    class Meta:
        model = Transaction
        fields = ["transaction_type", "type", "payment_method", "verified", "member", "cause", "year", "month"]


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ["reference", "receipt_number", "member__first_name", "member__last_name", "payment_reference"]
    ordering_fields = ["transaction_date", "amount", "created_at"]
    ordering = ["-transaction_date"]

    def get_queryset(self):
        return Transaction.objects.select_related(
            "member", "category", "cause", "pledge", "service",
            "bank_account", "recorded_by", "verified_by"
        ).filter(is_active=True)

    def get_serializer_class(self):
        if self.action == "list":
            return TransactionListSerializer
        return TransactionDetailSerializer

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsFinanceOrAbove])
    def verify(self, request, pk=None):
        tx = self.get_object()
        if tx.verified:
            return Response({"detail": "Already verified."}, status=400)
        tx.verified = True
        tx.verified_by = request.user
        tx.verified_at = timezone.now()
        tx.save(update_fields=["verified", "verified_by", "verified_at"])
        return Response({"detail": "Transaction verified."})

    @action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        """Download receipt PDF."""
        tx = self.get_object()
        if tx.receipt_pdf:
            return FileResponse(tx.receipt_pdf.open(), content_type="application/pdf",
                                as_attachment=True, filename=f"receipt-{tx.receipt_number}.pdf")
        # Generate on the fly
        from .utils import generate_receipt_pdf
        pdf_buffer = generate_receipt_pdf(tx, request)
        from django.http import HttpResponse
        response = HttpResponse(pdf_buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="receipt-{tx.receipt_number}.pdf"'
        return response

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Unified financial + member summary for the dashboard.
        Accepts ?period=this_month|last_month|this_year|all
        """
        from apps.members.models import Member, MemberStatus
        from apps.followup.models import FollowUpCase
        import datetime

        period = request.query_params.get("period", "this_month")
        today = timezone.now().date()

        # Determine date range
        if period == "this_month":
            date_from = today.replace(day=1)
            date_to = today
        elif period == "last_month":
            first_this = today.replace(day=1)
            date_to = first_this - datetime.timedelta(days=1)
            date_from = date_to.replace(day=1)
        elif period == "this_year":
            date_from = today.replace(month=1, day=1)
            date_to = today
        else:  # all
            date_from = None
            date_to = None

        qs = Transaction.objects.filter(is_active=True)
        if date_from:
            qs = qs.filter(transaction_date__gte=date_from)
        if date_to:
            qs = qs.filter(transaction_date__lte=date_to)

        income_types = [
            TransactionType.TITHE, TransactionType.OFFERING,
            TransactionType.DONATION, TransactionType.PLEDGE_PAYMENT,
            TransactionType.HALL_RENTAL, TransactionType.OTHER_INCOME,
        ]
        income_qs = qs.filter(transaction_type__in=income_types)
        expense_qs = qs.filter(transaction_type=TransactionType.EXPENSE)

        total_tithes    = income_qs.filter(transaction_type=TransactionType.TITHE).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")
        total_offerings = income_qs.filter(transaction_type=TransactionType.OFFERING).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")
        total_donations = income_qs.filter(transaction_type=TransactionType.DONATION).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")
        total_income    = income_qs.aggregate(t=Sum("amount"))["t"] or Decimal("0.00")
        total_expenses  = expense_qs.aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

        # This month totals (always)
        this_month_qs = Transaction.objects.filter(
            is_active=True,
            transaction_date__month=today.month,
            transaction_date__year=today.year,
            transaction_type__in=income_types,
        )
        this_month_total = this_month_qs.aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

        # Member stats
        member_qs = Member.objects.filter(is_active=True)
        active_members = member_qs.filter(membership_status=MemberStatus.ACTIVE).count()
        visitors       = member_qs.filter(membership_status=MemberStatus.VISITOR).count()
        inactive       = member_qs.filter(membership_status=MemberStatus.INACTIVE).count()
        transferred    = member_qs.filter(membership_status=MemberStatus.TRANSFERRED_OUT).count()

        # Open follow-ups
        open_followups = FollowUpCase.objects.filter(status__in=["open", "in_progress"]).count()

        # New members this month
        new_this_month = member_qs.filter(
            created_at__month=today.month,
            created_at__year=today.year,
        ).count()

        return Response({
            "period": period,
            "date_from": str(date_from) if date_from else None,
            "date_to": str(date_to) if date_to else None,
            # Finance
            "total_tithes":    float(total_tithes),
            "total_offerings": float(total_offerings),
            "total_donations": float(total_donations),
            "total_income":    float(total_income),
            "total_expenses":  float(total_expenses),
            "net_balance":     float(total_income - total_expenses),
            "this_month":      float(this_month_total),
            # Members
            "active_members":  active_members,
            "visitors":        visitors,
            "inactive":        inactive,
            "transferred":     transferred,
            "new_this_month":  new_this_month,
            # Pastoral
            "open_followups":  open_followups,
        })

    @action(detail=False, methods=["get"])
    def monthly_chart(self, request):
        """12-month income breakdown for chart display."""
        year = int(request.query_params.get("year", timezone.now().year))
        qs = Transaction.objects.filter(transaction_date__year=year, is_active=True)
        income_types = [
            TransactionType.TITHE, TransactionType.OFFERING,
            TransactionType.DONATION, TransactionType.PLEDGE_PAYMENT,
            TransactionType.HALL_RENTAL, TransactionType.OTHER_INCOME,
        ]
        income_qs = qs.filter(transaction_type__in=income_types)
        expense_qs = qs.filter(transaction_type=TransactionType.EXPENSE)

        labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        income_data, expense_data = [], []

        for m in range(1, 13):
            inc = income_qs.filter(transaction_date__month=m).aggregate(t=Sum("amount"))["t"] or 0
            exp = expense_qs.filter(transaction_date__month=m).aggregate(t=Sum("amount"))["t"] or 0
            income_data.append(float(inc))
            expense_data.append(float(exp))

        # Totals for doughnut chart
        tithes_total   = float(income_qs.filter(transaction_type=TransactionType.TITHE).aggregate(t=Sum("amount"))["t"] or 0)
        offerings_total= float(income_qs.filter(transaction_type=TransactionType.OFFERING).aggregate(t=Sum("amount"))["t"] or 0)
        donations_total= float(income_qs.filter(transaction_type__in=[TransactionType.DONATION, TransactionType.PLEDGE_PAYMENT]).aggregate(t=Sum("amount"))["t"] or 0)
        other_total    = float(income_qs.filter(transaction_type__in=[TransactionType.HALL_RENTAL, TransactionType.OTHER_INCOME]).aggregate(t=Sum("amount"))["t"] or 0)

        return Response({
            "year": year,
            "labels": labels,
            "income": income_data,
            "expenses": expense_data,
            "tithes_total": tithes_total,
            "offerings_total": offerings_total,
            "donations_total": donations_total,
            "other_total": other_total,
        })

    @action(detail=False, methods=["get"])
    def tithe_report(self, request):
        """Per-member tithe summary for a given year."""
        year = int(request.query_params.get("year", timezone.now().year))
        data = (
            Transaction.objects
            .filter(transaction_type=TransactionType.TITHE, transaction_date__year=year, is_active=True)
            .values("member__id", "member__first_name", "member__last_name", "member__member_number")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )
        return Response(list(data))


class FinanceCategoryViewSet(viewsets.ModelViewSet):
    queryset = FinanceCategory.objects.filter(is_active=True)
    serializer_class = FinanceCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ["transaction_type"]


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.filter(is_active=True)
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated, IsFinanceOrAbove]


class CauseViewSet(viewsets.ModelViewSet):
    queryset = Cause.objects.filter(is_active=True)
    serializer_class = CauseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=True, methods=["get"])
    def donors(self, request, pk=None):
        cause = self.get_object()
        data = (
            cause.transactions
            .filter(member__isnull=False)
            .values("member__id", "member__first_name", "member__last_name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        return Response(list(data))


class PledgeViewSet(viewsets.ModelViewSet):
    queryset = Pledge.objects.filter(is_active=True).select_related("member", "cause")
    serializer_class = PledgeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["cause", "is_fulfilled", "member"]

    @action(detail=False, methods=["get"])
    def outstanding(self, request):
        qs = self.get_queryset().filter(is_fulfilled=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
