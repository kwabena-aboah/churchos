from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserActivityLog

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "get_full_name", "role", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "phone", "avatar", "member")}),
        ("Permissions", {"fields": ("role", "cell_group", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "role", "password1", "password2")}),
    )
    readonly_fields = ["date_joined", "last_login"]

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "ip_address", "timestamp"]
    list_filter = ["action"]
    readonly_fields = ["user", "action", "description", "ip_address", "timestamp"]
    ordering = ["-timestamp"]
