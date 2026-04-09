from django.contrib import admin
from .models import ChurchSettings, ServiceType, Zone, CellGroup

@admin.register(ChurchSettings)
class ChurchSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ChurchSettings.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "day_of_week", "start_time", "is_recurring"]

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]

@admin.register(CellGroup)
class CellGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "zone", "meeting_day"]
    list_filter = ["zone"]
    search_fields = ["name"]
