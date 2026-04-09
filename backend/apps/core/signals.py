"""
Core Django signals for ChurchOS.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender="members.Member")
def member_post_save(sender, instance, created, **kwargs):
    """Send welcome message when a new member is created."""
    if not created:
        return
    try:
        from apps.core.models import ChurchSettings
        from apps.communication.models import MessageLog, MessageChannel, MessageTemplate
        church = ChurchSettings.load()
        template = MessageTemplate.objects.filter(
            event_type="WELCOME", channel=MessageChannel.EMAIL, is_default=True
        ).first()
        if template and instance.email and instance.receive_email:
            body = (template.body
                    .replace("{{first_name}}", instance.get_display_name())
                    .replace("{{church_name}}", church.church_name))
            subject = (template.subject
                       .replace("{{first_name}}", instance.get_display_name())
                       .replace("{{church_name}}", church.church_name))
            MessageLog.objects.create(
                member=instance, channel=MessageChannel.EMAIL,
                recipient=instance.email, subject=subject,
                body=body, event_type="WELCOME",
            )
    except Exception as e:
        logger.error(f"Welcome signal error: {e}")


@receiver(post_save, sender="finance.Transaction")
def transaction_post_save(sender, instance, created, **kwargs):
    """Send receipt notification when a new transaction is saved."""
    if not created or not instance.member:
        return
    try:
        from apps.core.models import ChurchSettings
        church = ChurchSettings.load()
        member = instance.member
        sym = church.currency_symbol
        msg = (
            f"Dear {member.get_display_name()}, your "
            f"{instance.get_transaction_type_display()} of "
            f"{sym}{instance.amount:,.2f} has been received. "
            f"Receipt No: {instance.receipt_number}. God bless you. — {church.church_name}"
        )
        from apps.communication.models import MessageLog, MessageChannel
        if church.enable_payment_receipt_sms and member.phone_primary and member.receive_sms:
            MessageLog.objects.create(
                member=member, channel=MessageChannel.SMS,
                recipient=member.phone_primary, body=msg[:160], event_type="RECEIPT",
            )
        if church.enable_payment_receipt_email and member.email and member.receive_email:
            MessageLog.objects.create(
                member=member, channel=MessageChannel.EMAIL,
                recipient=member.email,
                subject=f"Payment Receipt — {church.church_name}",
                body=msg, event_type="RECEIPT",
            )
    except Exception as e:
        logger.error(f"Receipt signal error: {e}")
