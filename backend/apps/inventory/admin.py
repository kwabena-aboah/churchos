from django.contrib import admin
from .models import ItemCategory, InventoryItem, ItemMovement

@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "condition", "quantity", "location", "purchase_price", "current_value"]
    list_filter = ["category", "condition", "department"]
    search_fields = ["name", "serial_number", "barcode"]

@admin.register(ItemMovement)
class ItemMovementAdmin(admin.ModelAdmin):
    list_display = ["item", "movement_type", "from_location", "to_location", "date", "performed_by"]
    list_filter = ["movement_type"]
    ordering = ["-date"]
