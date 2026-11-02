from django.contrib import admin
from .models import Transaction, FinanceCategory, BankAccount, Cause, Pledge, ExpenseApproval

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["reference", "transaction_type", "amount", "member", "transaction_date", "payment_method", "verified"]
    list_filter = ["transaction_type", "payment_method", "verified", "transaction_date"]
    search_fields = ["reference", "receipt_number", "member__first_name", "member__last_name", "payment_reference"]
    readonly_fields = ["reference", "receipt_number", "created_at", "updated_at"]
    ordering = ["-transaction_date"]
    date_hierarchy = "transaction_date"

@admin.register(FinanceCategory)
class FinanceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "transaction_type", "is_system"]
    list_filter = ["transaction_type"]

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ["name", "bank_name", "account_number", "currency", "current_balance", "is_default"]

@admin.register(Cause)
class CauseAdmin(admin.ModelAdmin):
    list_display = ["name", "target_amount", "start_date", "end_date", "is_ongoing"]

@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
    list_display = ["member", "cause", "pledge_amount", "amount_paid", "due_date", "is_fulfilled"]
    list_filter = ["is_fulfilled", "cause"]
