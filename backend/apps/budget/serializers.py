from rest_framework import serializers
from .models import BudgetYear, BudgetCategory, BudgetLine, BudgetAmendment


class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = "__all__"


class BudgetLineSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    department = serializers.CharField(source="category.department", read_only=True)

    class Meta:
        model = BudgetLine
        fields = "__all__"


class BudgetAmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetAmendment
        fields = "__all__"
        read_only_fields = ["approved_by", "approved_at"]


class BudgetYearSerializer(serializers.ModelSerializer):
    lines = BudgetLineSerializer(many=True, read_only=True)
    total_income_budget = serializers.ReadOnlyField()
    total_expense_budget = serializers.ReadOnlyField()

    class Meta:
        model = BudgetYear
        fields = "__all__"
