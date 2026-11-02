from django.contrib import admin
from .models import BudgetYear, BudgetCategory, BudgetLine, BudgetAmendment

@admin.register(BudgetYear)
class BudgetYearAdmin(admin.ModelAdmin):
    list_display = ["year", "title", "is_approved", "total_income_budget", "total_expense_budget"]
    list_filter = ["is_approved"]

@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "line_type", "sort_order"]
    list_filter = ["line_type", "department"]
    ordering = ["sort_order"]

@admin.register(BudgetLine)
class BudgetLineAdmin(admin.ModelAdmin):
    list_display = ["budget_year", "category", "line_type", "amount"]
    list_filter = ["budget_year", "line_type"]

@admin.register(BudgetAmendment)
class BudgetAmendmentAdmin(admin.ModelAdmin):
    list_display = ["budget_line", "old_amount", "new_amount", "approved_by", "approved_at"]
    readonly_fields = ["approved_at"]
