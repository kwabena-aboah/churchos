import io
from django.utils import timezone
from django.db.models import Q, Count
from django.http import FileResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from .models import Member, MemberDocument, MemberStatusHistory, MemberStatus
from .serializers import (
    MemberListSerializer, MemberDetailSerializer, MemberStatusChangeSerializer,
    MemberDocumentSerializer, MemberStatusHistorySerializer, MemberBirthdaySerializer,
)
from apps.core.permissions import IsAdminOrAbove, IsAdminOrReadOnly


class MemberFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method="filter_name")
    status = django_filters.CharFilter(field_name="membership_status")
    gender = django_filters.CharFilter(field_name="gender")
    zone = django_filters.UUIDFilter(field_name="zone__id")
    cell_group = django_filters.UUIDFilter(field_name="cell_group__id")
    birthday_month = django_filters.NumberFilter(field_name="date_of_birth__month")

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(middle_name__icontains=value) |
            Q(preferred_name__icontains=value) |
            Q(member_number__icontains=value)
        )

    class Meta:
        model = Member
        fields = ["name", "status", "gender", "zone", "cell_group", "birthday_month"]


class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MemberFilter
    search_fields = ["first_name", "last_name", "email", "phone_primary", "member_number"]
    ordering_fields = ["last_name", "first_name", "created_at", "membership_date"]
    ordering = ["last_name", "first_name"]

    def get_queryset(self):
        user = self.request.user
        qs = Member.objects.select_related("zone", "cell_group", "spouse")
        # Cell leaders only see their own cell group
        if user.role == "cell_leader" and user.cell_group:
            qs = qs.filter(cell_group=user.cell_group)
        return qs.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == "list":
            return MemberListSerializer
        return MemberDetailSerializer

    def perform_create(self, serializer):
        serializer.save()

    # ── Custom Actions ─────────────────────────────────────────────────────

    @action(detail=False, methods=["get"])
    def birthdays_today(self, request):
        today = timezone.now().date()
        qs = Member.objects.filter(
            date_of_birth__month=today.month,
            date_of_birth__day=today.day,
            membership_status__in=[MemberStatus.ACTIVE, MemberStatus.TRANSFERRED_IN],
            is_active=True,
        )
        serializer = MemberBirthdaySerializer(qs, many=True, context={"request": request})
        return Response({"count": qs.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def birthdays_this_month(self, request):
        today = timezone.now().date()
        qs = Member.objects.filter(
            date_of_birth__month=today.month,
            membership_status__in=[MemberStatus.ACTIVE, MemberStatus.TRANSFERRED_IN],
            is_active=True,
        ).order_by("date_of_birth__day")
        serializer = MemberBirthdaySerializer(qs, many=True, context={"request": request})
        return Response({"count": qs.count(), "results": serializer.data})

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        member = self.get_object()
        serializer = MemberStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        old_status = member.membership_status
        member.membership_status = data["new_status"]
        member.status_change_reason = data.get("reason", "")
        member.status_changed_date = data.get("effective_date", timezone.now().date())
        if data.get("transferred_to_church"):
            member.transferred_to_church = data["transferred_to_church"]
        member.save()

        MemberStatusHistory.objects.create(
            member=member,
            old_status=old_status,
            new_status=data["new_status"],
            reason=data.get("reason", ""),
            changed_by=request.user,
        )
        return Response(MemberDetailSerializer(member, context={"request": request}).data)

    @action(detail=True, methods=["get"])
    def status_history(self, request, pk=None):
        member = self.get_object()
        history = MemberStatusHistory.objects.filter(member=member)
        serializer = MemberStatusHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        member = self.get_object()
        docs = MemberDocument.objects.filter(member=member, is_active=True)
        serializer = MemberDocumentSerializer(docs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def upload_document(self, request, pk=None):
        member = self.get_object()
        serializer = MemberDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(member=member, uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def giving_summary(self, request, pk=None):
        """Returns a financial summary for this member."""
        member = self.get_object()
        from apps.finance.models import Transaction
        year = request.query_params.get("year", timezone.now().year)
        transactions = Transaction.objects.filter(member=member, transaction_date__year=year)
        summary = {}
        for tx in transactions:
            t = tx.transaction_type
            summary[t] = summary.get(t, 0) + float(tx.amount)
        return Response({"year": year, "member": str(member), "summary": summary})

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        qs = Member.objects.filter(is_active=True)
        by_status = dict(qs.values_list("membership_status").annotate(count=Count("id")))
        by_gender = dict(qs.filter(membership_status=MemberStatus.ACTIVE).values_list("gender").annotate(count=Count("id")))
        today = timezone.now().date()
        new_this_month = qs.filter(
            created_at__month=today.month,
            created_at__year=today.year,
        ).count()
        return Response({
            "total": qs.count(),
            "active": by_status.get(MemberStatus.ACTIVE, 0),
            "visitors": by_status.get(MemberStatus.VISITOR, 0),
            "inactive": by_status.get(MemberStatus.INACTIVE, 0),
            "by_status": by_status,
            "by_gender": by_gender,
            "new_this_month": new_this_month,
        })
