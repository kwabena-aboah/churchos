from rest_framework import serializers
from .models import ChurchSettings, ServiceType, Zone, CellGroup


class ChurchSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    ai_anthropic_api_key = serializers.CharField(
        write_only=True, required=False, allow_blank=True, max_length=1024
    )
    ai_openai_api_key = serializers.CharField(
        write_only=True, required=False, allow_blank=True, max_length=1024
    )
    has_ai_anthropic_api_key = serializers.SerializerMethodField()
    has_ai_openai_api_key = serializers.SerializerMethodField()
    clear_ai_anthropic_api_key = serializers.BooleanField(
        write_only=True, required=False
    )
    clear_ai_openai_api_key = serializers.BooleanField(
        write_only=True, required=False
    )

    class Meta:
        model = ChurchSettings
        exclude = [
            # Never expose integration keys via the public endpoint
            "paystack_secret_key",
            "twilio_auth_token",
            "sendgrid_api_key",
            "whatsapp_api_token",
        ]
        read_only_fields = ["id"]

    def get_logo_url(self, obj):
        request = self.context.get("request")
        return obj.get_logo_url(request)

    def get_favicon_url(self, obj):
        request = self.context.get("request")
        if obj.favicon:
            url = obj.favicon.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_has_ai_anthropic_api_key(self, obj):
        from .ai import get_ai_api_key

        return bool(get_ai_api_key("anthropic", obj))

    def get_has_ai_openai_api_key(self, obj):
        from .ai import get_ai_api_key

        return bool(get_ai_api_key("openai", obj))

    def update(self, instance, validated_data):
        clear_anthropic_key = validated_data.pop(
            "clear_ai_anthropic_api_key", False
        )
        clear_openai_key = validated_data.pop("clear_ai_openai_api_key", False)
        if clear_anthropic_key and "ai_anthropic_api_key" not in validated_data:
            validated_data["ai_anthropic_api_key"] = ""
        if clear_openai_key and "ai_openai_api_key" not in validated_data:
            validated_data["ai_openai_api_key"] = ""
        return super().update(instance, validated_data)


class ChurchSettingsPublicSerializer(serializers.ModelSerializer):
    """Minimal public-safe settings for the frontend shell (no keys)."""

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = ChurchSettings
        fields = [
            "church_name",
            "church_tagline",
            "church_denomination",
            "address",
            "city",
            "country",
            "phone",
            "email",
            "website",
            "logo_url",
            "primary_color",
            "secondary_color",
            "accent_color",
            "currency_code",
            "currency_symbol",
            "date_format",
            "time_zone",
            "enable_ai_features",
        ]

    def get_logo_url(self, obj):
        request = self.context.get("request")
        return obj.get_logo_url(request)


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = "__all__"


class ZoneSerializer(serializers.ModelSerializer):
    cell_group_count = serializers.SerializerMethodField()

    class Meta:
        model = Zone
        fields = "__all__"

    def get_cell_group_count(self, obj):
        return obj.cell_groups.filter(is_active=True).count()


class CellGroupSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)

    class Meta:
        model = CellGroup
        fields = "__all__"
