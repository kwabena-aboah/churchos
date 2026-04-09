from rest_framework import serializers
from .models import ChurchSettings, ServiceType, Zone, CellGroup


class ChurchSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()

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
