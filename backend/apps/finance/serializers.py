from rest_framework import serializers
from django.db.models import Sum
from .models import Transaction, FinanceCategory, BankAccount, Cause, Pledge, TransactionType


class FinanceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceCategory
        fields = "__all__"


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"


class CauseSerializer(serializers.ModelSerializer):
    total_raised = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    progress_percent = serializers.FloatField(read_only=True)
    donor_count = serializers.SerializerMethodField()

    class Meta:
        model = Cause
        fields = "__all__"

    def get_donor_count(self, obj):
        return obj.transactions.values("member").distinct().count()


class PledgeSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.get_full_name", read_only=True)
    member_number = serializers.CharField(source="member.member_number", read_only=True)
    cause_name = serializers.CharField(source="cause.name", read_only=True)
    balance_remaining = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Pledge
        fields = "__all__"


class TransactionListSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    member_number = serializers.CharField(source="member.member_number", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    cause_name = serializers.CharField(source="cause.name", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id", "reference", "receipt_number", "member_name", "member_number",
            "transaction_type", "category_name", "cause_name",
            "amount", "currency", "payment_method",
            "transaction_date", "verified", "recorded_by_name",
        ]

    def get_member_name(self, obj):
        return obj.member.get_full_name() if obj.member else "Anonymous"


class TransactionDetailSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)
    verified_by_name = serializers.CharField(source="verified_by.get_full_name", read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ["id", "reference", "receipt_number", "created_at", "updated_at", "recorded_by"]

    def get_member_name(self, obj):
        return obj.member.get_full_name() if obj.member else "Anonymous"


class FinanceSummarySerializer(serializers.Serializer):
    """Summary stats for finance dashboard."""
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net = serializers.DecimalField(max_digits=15, decimal_places=2)
    by_type = serializers.DictField()
    by_month = serializers.ListField()
    by_payment_method = serializers.DictField()
