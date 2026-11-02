from django.contrib import admin
from .models import Member, MemberDocument, MemberStatusHistory

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["member_number", "get_full_name", "phone_primary", "membership_status", "zone", "cell_group", "created_at"]
    list_filter = ["membership_status", "gender", "zone", "cell_group"]
    search_fields = ["first_name", "last_name", "email", "phone_primary", "member_number"]
    readonly_fields = ["member_number", "created_at", "updated_at"]
    ordering = ["last_name", "first_name"]
    fieldsets = (
        ("Identity", {"fields": ("member_number", "first_name", "middle_name", "last_name", "preferred_name", "gender", "date_of_birth", "photo", "national_id")}),
        ("Contact", {"fields": ("phone_primary", "phone_secondary", "email", "whatsapp_number", "address", "city", "region", "country")}),
        ("Membership", {"fields": ("membership_status", "membership_date", "visitor_date", "zone", "cell_group")}),
        ("Spiritual", {"fields": ("salvation_date", "baptism_date", "baptism_type", "ministry_interests", "spiritual_gifts")}),
        ("Professional", {"fields": ("occupation", "employer", "education_level")}),
        ("Emergency", {"fields": ("emergency_contact_name", "emergency_contact_phone", "emergency_contact_relationship")}),
        ("Preferences", {"fields": ("receive_sms", "receive_email", "receive_whatsapp", "notes")}),
    )

@admin.register(MemberStatusHistory)
class MemberStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["member", "old_status", "new_status", "changed_by", "changed_at"]
    readonly_fields = ["member", "old_status", "new_status", "changed_by", "changed_at"]
    ordering = ["-changed_at"]
