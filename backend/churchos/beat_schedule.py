"""
ChurchOS Celery Beat Schedule
Add to settings/base.py or configure via Django Admin (django-celery-beat).
"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Birthday greetings — every day at 6 AM
    "birthday-greetings": {
        "task": "send_birthday_greetings",
        "schedule": crontab(hour=6, minute=0),
    },
    # Absentee detection — every Monday at 7 AM
    "absentee-detection": {
        "task": "detect_absentee_members",
        "schedule": crontab(hour=7, minute=0, day_of_week=1),
    },
    # Daily audit — every day at 2 AM
    "daily-audit": {
        "task": "run_daily_audit",
        "schedule": crontab(hour=2, minute=0),
    },
    # Event reminders — every hour (checks for events starting in ~24h)
    "event-reminders": {
        "task": "send_event_reminders",
        "schedule": crontab(minute=0),  # Every hour
    },
    # Pledge reminders — every day at 8 AM
    "pledge-reminders": {
        "task": "send_pledge_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    # AI weekly briefing — every Monday at 7:30 AM
    "ai-weekly-briefing": {
        "task": "generate_ai_weekly_briefing",
        "schedule": crontab(hour=7, minute=30, day_of_week=1),
    },
}
