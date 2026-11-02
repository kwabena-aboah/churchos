from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MessageTemplate, MessageLog, Broadcast, MessageChannel
from .serializers import MessageTemplateSerializer, MessageLogSerializer, BroadcastSerializer
from apps.core.permissions import IsAdminOrReadOnly
import logging

logger = logging.getLogger(__name__)


def send_sms(recipient, body, log_obj=None):
    """Send SMS via Twilio."""
    from apps.core.models import ChurchSettings
    from django.conf import settings
    try:
        church = ChurchSettings.load()
        if not church.twilio_account_sid:
            raise ValueError("Twilio not configured")
        from twilio.rest import Client
        client = Client(church.twilio_account_sid, church.twilio_auth_token)
        msg = client.messages.create(body=body, from_=church.twilio_sender_id, to=recipient)
        if log_obj:
            log_obj.status = "sent"
            log_obj.provider_reference = msg.sid
            log_obj.sent_at = timezone.now()
            log_obj.save()
        return True
    except Exception as e:
        logger.error(f"SMS send failed: {e}")
        if log_obj:
            log_obj.status = "failed"
            log_obj.error_message = str(e)
            log_obj.save()
        return False


def send_whatsapp(recipient, body, log_obj=None):
    """Send WhatsApp message via Meta Cloud API."""
    from apps.core.models import ChurchSettings
    import requests
    try:
        church = ChurchSettings.load()
        if not church.whatsapp_api_token:
            raise ValueError("WhatsApp not configured")
        url = f"https://graph.facebook.com/v18.0/{church.whatsapp_phone_id}/messages"
        headers = {"Authorization": f"Bearer {church.whatsapp_api_token}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "to": recipient, "type": "text", "text": {"body": body}}
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            if log_obj:
                log_obj.status = "sent"
                log_obj.provider_reference = resp.json().get("messages", [{}])[0].get("id", "")
                log_obj.sent_at = timezone.now()
                log_obj.save()
            return True
        raise Exception(resp.text)
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        if log_obj:
            log_obj.status = "failed"
            log_obj.error_message = str(e)
            log_obj.save()
        return False


def send_email(recipient, subject, body, is_html=False, log_obj=None):
    """Send email via Django's email backend."""
    from django.core.mail import send_mail
    try:
        send_mail(subject=subject, message=body if not is_html else "", html_message=body if is_html else None, from_email=None, recipient_list=[recipient], fail_silently=False)
        if log_obj:
            log_obj.status = "sent"
            log_obj.sent_at = timezone.now()
            log_obj.save()
        return True
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        if log_obj:
            log_obj.status = "failed"
            log_obj.error_message = str(e)
            log_obj.save()
        return False


class MessageTemplateViewSet(viewsets.ModelViewSet):
    queryset = MessageTemplate.objects.filter(is_active=True)
    serializer_class = MessageTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ["channel", "event_type"]


class MessageLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MessageLog.objects.all().select_related("member", "sent_by")
    serializer_class = MessageLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["channel", "status", "event_type"]
    search_fields = ["recipient", "subject"]

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, pk=None):
        log = self.get_object()
        if log.channel == MessageChannel.SMS:
            success = send_sms(log.recipient, log.body, log)
        elif log.channel == MessageChannel.WHATSAPP:
            success = send_whatsapp(log.recipient, log.body, log)
        elif log.channel == MessageChannel.EMAIL:
            success = send_email(log.recipient, log.subject, log.body, log_obj=log)
        else:
            return Response({"error": "Unknown channel"}, status=400)
        return Response({"success": success})


class BroadcastViewSet(viewsets.ModelViewSet):
    queryset = Broadcast.objects.all()
    serializer_class = BroadcastSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(sent_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="send")
    def send_broadcast(self, request, pk=None):
        broadcast = self.get_object()
        if broadcast.status == "sent":
            return Response({"error": "Already sent."}, status=400)

        from apps.members.models import Member, MemberStatus
        members = Member.objects.filter(is_active=True)
        if broadcast.target_group == "all_active":
            members = members.filter(membership_status=MemberStatus.ACTIVE)
        elif broadcast.target_group == "cell_group" and broadcast.target_cell_group:
            members = members.filter(cell_group=broadcast.target_cell_group)
        elif broadcast.target_group == "zone" and broadcast.target_zone:
            members = members.filter(zone=broadcast.target_zone)
        elif broadcast.target_group == "visitors":
            members = members.filter(membership_status=MemberStatus.VISITOR)

        count = 0
        for member in members:
            body = broadcast.body.replace("{{first_name}}", member.get_display_name()).replace("{{church_name}}", "")
            for channel in broadcast.channels:
                log = MessageLog.objects.create(
                    member=member, channel=channel,
                    recipient=member.phone_primary if channel in ["sms", "whatsapp"] else member.email,
                    subject=broadcast.subject, body=body,
                    event_type="BROADCAST", sent_by=request.user,
                )
                if channel == "sms" and member.receive_sms:
                    send_sms(member.phone_primary, body, log)
                elif channel == "whatsapp" and member.receive_whatsapp:
                    send_whatsapp(member.get_whatsapp_number(), body, log)
                elif channel == "email" and member.email and member.receive_email:
                    send_email(member.email, broadcast.subject, body, log_obj=log)
            count += 1

        broadcast.status = "sent"
        broadcast.sent_at = timezone.now()
        broadcast.recipient_count = count
        broadcast.save()
        return Response({"status": "sent", "recipient_count": count})
