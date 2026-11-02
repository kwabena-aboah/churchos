from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import FollowUpCase, FollowUpLog
from apps.core.permissions import IsPastorOrAbove


class FollowUpLogSerializer(serializers.ModelSerializer):
    logged_by_name = serializers.CharField(source="logged_by.get_full_name", read_only=True)

    class Meta:
        model = FollowUpLog
        fields = "__all__"


class FollowUpCaseSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.get_full_name", read_only=True)
    member_phone = serializers.CharField(source="member.phone_primary", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    logs = FollowUpLogSerializer(many=True, read_only=True)
    log_count = serializers.SerializerMethodField()

    class Meta:
        model = FollowUpCase
        fields = "__all__"
        read_only_fields = ["created_by"]

    def get_log_count(self, obj):
        return obj.logs.count()


class FollowUpCaseViewSet(viewsets.ModelViewSet):
    queryset = FollowUpCase.objects.all().select_related("member", "assigned_to")
    serializer_class = FollowUpCaseSerializer
    permission_classes = [IsAuthenticated, IsPastorOrAbove]
    filterset_fields = ["case_type", "priority", "status", "assigned_to"]
    search_fields = ["member__first_name", "member__last_name", "description"]
    ordering_fields = ["created_at", "priority", "target_date"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "cell_leader" and self.request.user.cell_group:
            qs = qs.filter(member__cell_group=self.request.user.cell_group)
        return qs

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        case = self.get_object()
        case.status = "closed"
        case.closed_at = timezone.now()
        case.closure_notes = request.data.get("closure_notes", "")
        case.save()
        return Response({"status": "closed"})

    @action(detail=True, methods=["post"], url_path="add-log")
    def add_log(self, request, pk=None):
        case = self.get_object()
        serializer = FollowUpLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(case=case, logged_by=request.user)
        case.status = "in_progress"
        case.save(update_fields=["status"])
        return Response(serializer.data, status=201)


class FollowUpLogViewSet(viewsets.ModelViewSet):
    queryset = FollowUpLog.objects.all().select_related("case", "logged_by")
    serializer_class = FollowUpLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["case", "contact_method"]

    def perform_create(self, serializer):
        serializer.save(logged_by=self.request.user)
