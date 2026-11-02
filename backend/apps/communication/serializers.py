from rest_framework import serializers
from .models import MessageTemplate, MessageLog, Broadcast


class MessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTemplate
        fields = "__all__"


class MessageLogSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()

    class Meta:
        model = MessageLog
        fields = "__all__"

    def get_member_name(self, obj):
        return obj.member.get_full_name() if obj.member else None


class BroadcastSerializer(serializers.ModelSerializer):
    sent_by_name = serializers.CharField(source="sent_by.get_full_name", read_only=True)

    class Meta:
        model = Broadcast
        fields = "__all__"
        read_only_fields = ["sent_at", "recipient_count", "sent_by", "status"]
