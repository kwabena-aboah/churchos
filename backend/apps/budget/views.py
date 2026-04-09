from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BudgetYear, BudgetCategory, BudgetLine, BudgetAmendment
from .serializers import BudgetYearSerializer, BudgetCategorySerializer, BudgetLineSerializer, BudgetAmendmentSerializer
from apps.core.permissions import IsFinanceOrAbove, IsAdminOrReadOnly


class BudgetYearViewSet(viewsets.ModelViewSet):
    queryset = BudgetYear.objects.filter(is_active=True)
    serializer_class = BudgetYearSerializer
    permission_classes = [IsAuthenticated, IsFinanceOrAbove]
    ordering_fields = ["year"]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        budget = self.get_object()
        from django.utils import timezone
        budget.is_approved = True
        budget.approved_by = request.user
        budget.approved_at = timezone.now()
        budget.save()
        return Response({"status": "approved"})


class BudgetCategoryViewSet(viewsets.ModelViewSet):
    queryset = BudgetCategory.objects.filter(is_active=True)
    serializer_class = BudgetCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ["line_type", "department"]


class BudgetLineViewSet(viewsets.ModelViewSet):
    queryset = BudgetLine.objects.filter(is_active=True).select_related("budget_year", "category")
    serializer_class = BudgetLineSerializer
    permission_classes = [IsAuthenticated, IsFinanceOrAbove]
    filterset_fields = ["budget_year", "line_type", "category"]


class BudgetAmendmentViewSet(viewsets.ModelViewSet):
    queryset = BudgetAmendment.objects.all().select_related("budget_line", "approved_by")
    serializer_class = BudgetAmendmentSerializer
    permission_classes = [IsAuthenticated, IsFinanceOrAbove]

    def perform_create(self, serializer):
        serializer.save(approved_by=self.request.user)
