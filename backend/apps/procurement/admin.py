from django.contrib import admin
from .models import Vendor, PurchaseRequest, PurchaseRequestItem, PurchaseOrder

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_person", "phone", "category", "rating"]
    search_fields = ["name", "contact_person"]

class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItem
    extra = 1

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ["reference", "title", "department", "total_estimated", "status", "requested_by", "created_at"]
    list_filter = ["status", "department"]
    search_fields = ["reference", "title"]
    inlines = [PurchaseRequestItemInline]
    readonly_fields = ["reference"]

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["reference", "vendor", "total_amount", "status", "order_date", "expected_delivery"]
    list_filter = ["status", "vendor"]
    readonly_fields = ["reference"]
