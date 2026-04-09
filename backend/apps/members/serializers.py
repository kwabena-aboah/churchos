from rest_framework import serializers
from .models import Member, MemberDocument, MemberStatusHistory, MemberStatus


class MemberListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    full_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    cell_group_name = serializers.CharField(source="cell_group.name", read_only=True)

    class Meta:
        model = Member
        fields = [
            "id", "member_number", "full_name", "first_name", "last_name",
            "gender", "phone_primary", "email", "membership_status",
            "photo_url", "age", "date_of_birth", "zone_name", "cell_group_name",
            "is_active", "created_at",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        return None


class MemberDetailSerializer(serializers.ModelSerializer):
    """Full serializer for create/retrieve/update."""
    full_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)
    years_as_member = serializers.IntegerField(read_only=True)
    is_birthday_today = serializers.BooleanField(read_only=True)
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    cell_group_name = serializers.CharField(source="cell_group.name", read_only=True)

    class Meta:
        model = Member
        fields = "__all__"
        read_only_fields = ["id", "member_number", "created_at", "updated_at"]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        return None


class MemberStatusChangeSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=MemberStatus.choices)
    reason = serializers.CharField(required=False, allow_blank=True)
    effective_date = serializers.DateField(required=False)
    transferred_to_church = serializers.CharField(required=False, allow_blank=True)


class MemberDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberDocument
        fields = "__all__"
        read_only_fields = ["id", "uploaded_by"]


class MemberStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.get_full_name", read_only=True)

    class Meta:
        model = MemberStatusHistory
        fields = "__all__"


class MemberBirthdaySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)
    whatsapp_number = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id", "member_number", "full_name", "date_of_birth",
            "age", "phone_primary", "whatsapp_number", "email",
            "receive_sms", "receive_email", "receive_whatsapp",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_whatsapp_number(self, obj):
        return obj.get_whatsapp_number()
