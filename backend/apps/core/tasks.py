"""
ChurchOS Celery Tasks
Handles: birthday greetings, anniversary messages, audit runs, AI briefings
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(name="send_birthday_greetings")
def send_birthday_greetings():
    """Run daily at 6 AM — send birthday greetings to members."""
    from apps.members.models import Member, MemberStatus
    from apps.core.models import ChurchSettings
    from apps.communication.models import MessageLog, MessageTemplate, MessageChannel
    from apps.communication.views import send_sms, send_email, send_whatsapp

    church = ChurchSettings.load()
    today = timezone.now().date()

    members = Member.objects.filter(
        is_active=True,
        membership_status__in=[MemberStatus.ACTIVE, MemberStatus.VISITOR],
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
    )

    sent_count = 0
    for member in members:
        name = member.get_display_name()
        body = f"Happy Birthday, {name}! 🎂 Wishing you God's abundant blessings on your special day. — {church.church_name}"

        if church.enable_birthday_email and member.email and member.receive_email:
            log = MessageLog.objects.create(
                member=member, channel=MessageChannel.EMAIL,
                recipient=member.email,
                subject=f"Happy Birthday, {name}! 🎂",
                body=body, event_type="BIRTHDAY",
            )
            send_email(member.email, log.subject, body, log_obj=log)

        if church.enable_birthday_sms and member.phone_primary and member.receive_sms:
            log = MessageLog.objects.create(
                member=member, channel=MessageChannel.SMS,
                recipient=member.phone_primary,
                body=body, event_type="BIRTHDAY",
            )
            send_sms(member.phone_primary, body, log)

        if church.enable_birthday_whatsapp and member.receive_whatsapp:
            number = member.get_whatsapp_number()
            log = MessageLog.objects.create(
                member=member, channel=MessageChannel.WHATSAPP,
                recipient=number, body=body, event_type="BIRTHDAY",
            )
            send_whatsapp(number, body, log)

        sent_count += 1

    logger.info(f"Birthday greetings sent to {sent_count} members on {today}.")
    return sent_count


@shared_task(name="send_anniversary_greetings")
def send_anniversary_greetings():
    """Run daily — send wedding anniversary greetings."""
    from apps.members.models import Member, MemberStatus
    from apps.core.models import ChurchSettings
    from apps.communication.models import MessageLog, MessageChannel
    from apps.communication.views import send_sms

    church = ChurchSettings.load()
    today = timezone.now().date()

    # Members with wedding anniversary today (use salvation_date as proxy — adapt as needed)
    # In production, add a wedding_anniversary_date field to Member
    logger.info("Anniversary greetings task completed.")


@shared_task(name="detect_absentee_members")
def detect_absentee_members():
    """
    Weekly — flag members absent for 2+ consecutive Sundays.
    Creates follow-up cases automatically.
    """
    from apps.members.models import Member, MemberStatus
    from apps.events.models import EventAttendance
    from apps.followup.models import FollowUpCase
    from django.db.models import Q
    import datetime

    today = timezone.now().date()
    two_sundays_ago = today - datetime.timedelta(weeks=2)

    active_members = Member.objects.filter(
        is_active=True, membership_status=MemberStatus.ACTIVE
    )

    flagged = 0
    for member in active_members:
        recent_attendance = EventAttendance.objects.filter(
            member=member,
            date__gte=two_sundays_ago,
        ).exists()

        if not recent_attendance:
            # Don't duplicate open cases
            existing = FollowUpCase.objects.filter(
                member=member, case_type="absentee", status__in=["open", "in_progress"]
            ).exists()
            if not existing:
                FollowUpCase.objects.create(
                    member=member,
                    case_type="absentee",
                    priority="medium",
                    status="open",
                    description=f"Member has not attended services for 2+ weeks (detected {today}).",
                )
                flagged += 1

    logger.info(f"Absentee detection: {flagged} new cases created.")
    return flagged


@shared_task(name="run_daily_audit")
def run_daily_audit():
    """Run all daily audit checks."""
    from apps.audit.models import AuditCheck
    from apps.audit.views import run_single_check

    checks = AuditCheck.objects.filter(is_active=True, is_enabled=True, run_schedule="daily")
    results = []
    for check in checks:
        try:
            report = run_single_check(check)
            if report:
                results.append({"check": check.name, "status": report.status})
        except Exception as e:
            logger.error(f"Audit check '{check.name}' failed: {e}")

    fail_count = sum(1 for r in results if r["status"] == "fail")
    if fail_count > 0:
        _notify_admins_of_audit_failures(results)

    logger.info(f"Daily audit complete: {len(results)} checks, {fail_count} failures.")
    return results


def _notify_admins_of_audit_failures(results):
    """Email super admins when audit checks fail."""
    from apps.communication.views import send_email
    from django.contrib.auth import get_user_model
    from apps.accounts.constants import Role

    User = get_user_model()
    admins = User.objects.filter(role__in=[Role.SUPER_ADMIN, Role.ADMINISTRATOR], is_active=True)
    failures = [r for r in results if r["status"] in ["fail", "warning"]]
    if not failures:
        return

    body = "ChurchOS Audit Alert\n\nThe following issues were detected:\n\n"
    for f in failures:
        body += f"• {f['check']}: {f['status'].upper()}\n"
    body += "\nPlease log in to review and resolve these issues."

    for admin in admins:
        if admin.email:
            send_email(admin.email, "⚠️ ChurchOS Audit Alert", body)


@shared_task(name="send_event_reminders")
def send_event_reminders():
    """Send reminders 24 hours before events with registration."""
    from apps.events.models import Event, EventRegistration
    from apps.communication.models import MessageLog, MessageChannel
    from apps.communication.views import send_email, send_sms
    import datetime

    now = timezone.now()
    in_24h = now + datetime.timedelta(hours=24)
    window_start = now + datetime.timedelta(hours=23)

    upcoming = Event.objects.filter(
        is_active=True,
        send_reminders=True,
        requires_registration=True,
        start_datetime__range=(window_start, in_24h),
    )

    for event in upcoming:
        registrations = EventRegistration.objects.filter(
            event=event, status="confirmed"
        ).select_related("member")
        for reg in registrations:
            if not reg.member:
                continue
            body = (f"Reminder: '{event.title}' is tomorrow at "
                    f"{event.start_datetime.strftime('%I:%M %p')}. "
                    f"Venue: {event.venue_name or 'Church Premises'}. "
                    f"Your ticket ref: {reg.ticket_ref}")
            if reg.member.email and reg.member.receive_email:
                log = MessageLog.objects.create(
                    member=reg.member, channel=MessageChannel.EMAIL,
                    recipient=reg.member.email,
                    subject=f"Reminder: {event.title}",
                    body=body, event_type="EVENT_REMINDER",
                )
                send_email(reg.member.email, log.subject, body, log_obj=log)


@shared_task(name="send_pledge_reminders")
def send_pledge_reminders():
    """Remind members of unfulfilled pledges due within 7 days."""
    from apps.finance.models import Pledge
    from apps.communication.models import MessageLog, MessageChannel
    from apps.communication.views import send_email, send_sms
    from apps.core.models import ChurchSettings
    import datetime

    church = ChurchSettings.load()
    today = timezone.now().date()
    in_7_days = today + datetime.timedelta(days=7)

    pledges = Pledge.objects.filter(
        is_active=True, is_fulfilled=False,
        due_date__range=(today, in_7_days),
    ).select_related("member", "cause")

    for pledge in pledges:
        member = pledge.member
        balance = pledge.balance_remaining
        cause_name = pledge.cause.name if pledge.cause else "your pledge"
        body = (f"Dear {member.get_display_name()}, your pledge of "
                f"{church.currency_symbol}{pledge.pledge_amount} towards {cause_name} "
                f"is due on {pledge.due_date}. Balance remaining: {church.currency_symbol}{balance}. "
                f"Thank you for your faithfulness. — {church.church_name}")

        if member.email and member.receive_email:
            log = MessageLog.objects.create(
                member=member, channel=MessageChannel.EMAIL,
                recipient=member.email,
                subject=f"Pledge Reminder — {church.church_name}",
                body=body, event_type="PLEDGE_REMINDER",
            )
            send_email(member.email, log.subject, body, log_obj=log)

        if member.phone_primary and member.receive_sms:
            log = MessageLog.objects.create(
                member=member, channel=MessageChannel.SMS,
                recipient=member.phone_primary,
                body=body[:160], event_type="PLEDGE_REMINDER",
            )
            send_sms(member.phone_primary, body[:160], log)


@shared_task(name="generate_ai_weekly_briefing")
def generate_ai_weekly_briefing():
    """
    Monday morning: generate AI briefing for pastors/admins.
    Summarises: finances, attendance, follow-ups, upcoming events.
    """
    from apps.core.models import ChurchSettings
    from apps.communication.views import send_email
    from django.conf import settings
    import datetime

    church = ChurchSettings.load()
    if not church.ai_weekly_briefing or not settings.ANTHROPIC_API_KEY:
        return "AI briefing disabled or not configured."

    today = timezone.now().date()
    last_week = today - datetime.timedelta(days=7)

    # Gather stats
    from apps.members.models import Member, MemberStatus
    from apps.finance.models import Transaction, TransactionType
    from apps.followup.models import FollowUpCase
    from apps.events.models import Event
    from django.db.models import Sum

    total_members = Member.objects.filter(is_active=True, membership_status=MemberStatus.ACTIVE).count()
    new_this_week = Member.objects.filter(created_at__date__gte=last_week).count()
    income_week = Transaction.objects.filter(
        transaction_date__gte=last_week,
        transaction_type__in=[TransactionType.TITHE, TransactionType.OFFERING, TransactionType.DONATION]
    ).aggregate(total=Sum("amount"))["total"] or 0
    open_cases = FollowUpCase.objects.filter(status__in=["open", "in_progress"]).count()
    upcoming_events = Event.objects.filter(
        is_active=True, start_datetime__date__range=(today, today + datetime.timedelta(days=7))
    ).count()

    context = f"""
Church: {church.church_name}
Week ending: {today}

STATISTICS:
- Total active members: {total_members}
- New members this week: {new_this_week}
- Income this week: {church.currency_symbol}{income_week:,.2f}
- Open follow-up cases: {open_cases}
- Events this coming week: {upcoming_events}
"""

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""You are a pastoral assistant. Write a concise, warm weekly briefing for the church leadership based on the following data. 
Use plain text (no markdown). Include highlights, any areas of concern, and one encouraging note.

{context}"""
            }]
        )
        briefing_text = message.content[0].text
    except Exception as e:
        briefing_text = f"AI briefing generation failed: {e}\n\n{context}"

    # Send to configured recipients
    recipients = [r.strip() for r in church.ai_briefing_recipients.split(",") if r.strip()]
    for email in recipients:
        send_email(
            email,
            f"📋 ChurchOS Weekly Briefing — {today.strftime('%B %d, %Y')}",
            briefing_text,
        )

    logger.info(f"AI weekly briefing sent to {len(recipients)} recipients.")
    return f"Sent to {len(recipients)} recipients."
