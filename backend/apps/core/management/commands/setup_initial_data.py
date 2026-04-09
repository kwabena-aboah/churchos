"""
Management command to seed initial ChurchOS data:
- Default church settings
- Finance categories
- Service types
- Audit checks
- Default message templates
"""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Create initial ChurchOS data (categories, service types, audit checks, templates)"

    def handle(self, *args, **options):
        self.setup_settings()
        self.setup_service_types()
        self.setup_finance_categories()
        self.setup_budget_categories()
        self.setup_audit_checks()
        self.setup_message_templates()
        self.stdout.write(self.style.SUCCESS("✅ ChurchOS initial data setup complete."))

    def setup_settings(self):
        from apps.core.models import ChurchSettings
        s, created = ChurchSettings.objects.get_or_create(pk=1)
        if created:
            s.church_name = "My Church"
            s.member_number_prefix = "CHR"
            s.currency_code = "GHS"
            s.currency_symbol = "₵"
            s.save()
            self.stdout.write("  ✓ Church settings created")
        else:
            self.stdout.write("  · Church settings already exist")

    def setup_service_types(self):
        from apps.core.models import ServiceType
        services = [
            {"name": "Sunday Service", "day_of_week": 6, "is_recurring": True, "color": "#1a6b3c"},
            {"name": "Midweek Service", "day_of_week": 2, "is_recurring": True, "color": "#2563eb"},
            {"name": "Prayer Meeting", "day_of_week": 4, "is_recurring": True, "color": "#7c3aed"},
            {"name": "Special Service", "day_of_week": None, "is_recurring": False, "color": "#c9a84c"},
            {"name": "Youth Service", "day_of_week": 5, "is_recurring": True, "color": "#dc2626"},
        ]
        count = 0
        for s in services:
            _, created = ServiceType.objects.get_or_create(name=s["name"], defaults=s)
            if created:
                count += 1
        self.stdout.write(f"  ✓ {count} service types created")

    def setup_finance_categories(self):
        from apps.finance.models import FinanceCategory, TransactionType
        categories = [
            # Income
            {"name": "Sunday Tithe", "transaction_type": TransactionType.TITHE, "color": "#1a6b3c", "is_system": True},
            {"name": "Midweek Tithe", "transaction_type": TransactionType.TITHE, "color": "#15803d", "is_system": True},
            {"name": "Sunday Offering", "transaction_type": TransactionType.OFFERING, "color": "#c9a84c", "is_system": True},
            {"name": "Special Offering", "transaction_type": TransactionType.OFFERING, "color": "#b45309", "is_system": True},
            {"name": "Harvest Offering", "transaction_type": TransactionType.OFFERING, "color": "#92400e", "is_system": False},
            {"name": "General Donation", "transaction_type": TransactionType.DONATION, "color": "#2563eb", "is_system": True},
            {"name": "Building Fund", "transaction_type": TransactionType.DONATION, "color": "#1d4ed8", "is_system": False},
            {"name": "Welfare Fund", "transaction_type": TransactionType.DONATION, "color": "#7c3aed", "is_system": False},
            {"name": "Hall Rental", "transaction_type": TransactionType.HALL_RENTAL, "color": "#0f766e", "is_system": True},
            {"name": "Sales", "transaction_type": TransactionType.OTHER_INCOME, "color": "#0891b2", "is_system": False},
            # Expense
            {"name": "Staff Salary", "transaction_type": TransactionType.EXPENSE, "color": "#dc2626", "is_system": True},
            {"name": "Utilities", "transaction_type": TransactionType.EXPENSE, "color": "#b91c1c", "is_system": True},
            {"name": "Maintenance & Repairs", "transaction_type": TransactionType.EXPENSE, "color": "#991b1b", "is_system": False},
            {"name": "Office Supplies", "transaction_type": TransactionType.EXPENSE, "color": "#7f1d1d", "is_system": False},
            {"name": "Outreach & Evangelism", "transaction_type": TransactionType.EXPENSE, "color": "#f97316", "is_system": False},
            {"name": "Welfare Support", "transaction_type": TransactionType.EXPENSE, "color": "#ea580c", "is_system": False},
            {"name": "Events & Programs", "transaction_type": TransactionType.EXPENSE, "color": "#c2410c", "is_system": False},
            {"name": "Miscellaneous", "transaction_type": TransactionType.EXPENSE, "color": "#6b7280", "is_system": False},
        ]
        count = 0
        for c in categories:
            _, created = FinanceCategory.objects.get_or_create(
                name=c["name"], transaction_type=c["transaction_type"],
                defaults=c
            )
            if created:
                count += 1
        self.stdout.write(f"  ✓ {count} finance categories created")

    def setup_budget_categories(self):
        from apps.budget.models import BudgetCategory
        categories = [
            {"name": "Tithes", "line_type": "income", "department": "Finance", "sort_order": 1},
            {"name": "Offerings", "line_type": "income", "department": "Finance", "sort_order": 2},
            {"name": "Donations", "line_type": "income", "department": "Finance", "sort_order": 3},
            {"name": "Hall Rentals", "line_type": "income", "department": "Finance", "sort_order": 4},
            {"name": "Other Income", "line_type": "income", "department": "Finance", "sort_order": 5},
            {"name": "Staff Salaries", "line_type": "expense", "department": "Administration", "sort_order": 10},
            {"name": "Utilities", "line_type": "expense", "department": "Administration", "sort_order": 11},
            {"name": "Maintenance", "line_type": "expense", "department": "Administration", "sort_order": 12},
            {"name": "Office & Admin", "line_type": "expense", "department": "Administration", "sort_order": 13},
            {"name": "Outreach & Missions", "line_type": "expense", "department": "Ministry", "sort_order": 20},
            {"name": "Youth Ministry", "line_type": "expense", "department": "Ministry", "sort_order": 21},
            {"name": "Welfare Fund", "line_type": "expense", "department": "Welfare", "sort_order": 30},
            {"name": "Events & Programs", "line_type": "expense", "department": "Programs", "sort_order": 40},
            {"name": "Equipment & IT", "line_type": "expense", "department": "Administration", "sort_order": 50},
            {"name": "Miscellaneous", "line_type": "expense", "department": "General", "sort_order": 99},
        ]
        count = 0
        for c in categories:
            _, created = BudgetCategory.objects.get_or_create(name=c["name"], line_type=c["line_type"], defaults=c)
            if created:
                count += 1
        self.stdout.write(f"  ✓ {count} budget categories created")

    def setup_audit_checks(self):
        from apps.audit.models import AuditCheck
        checks = [
            {
                "name": "Unreceipted Transactions",
                "category": "finance", "severity": "warning",
                "check_function": "run_check_unreceipted_transactions",
                "description": "Flags transactions older than 7 days that have no receipt PDF attached.",
                "run_schedule": "daily",
            },
            {
                "name": "Unverified High-Value Expenses",
                "category": "finance", "severity": "critical",
                "check_function": "run_check_unverified_transactions",
                "description": "Flags expenses above the approval threshold that have no secondary verification.",
                "run_schedule": "daily",
            },
            {
                "name": "Members Without Contact Information",
                "category": "data", "severity": "warning",
                "check_function": "run_check_members_no_contact",
                "description": "Active members with neither a phone number nor email address on file.",
                "run_schedule": "weekly",
            },
            {
                "name": "Workers Missing Payroll",
                "category": "compliance", "severity": "warning",
                "check_function": "run_check_workers_no_payroll",
                "description": "Active full-time or part-time workers with no payslip in the last 60 days.",
                "run_schedule": "monthly",
            },
            {
                "name": "Stale Purchase Orders",
                "category": "finance", "severity": "warning",
                "check_function": "run_check_open_procurement",
                "description": "Purchase orders that have been open for more than 30 days without being received.",
                "run_schedule": "weekly",
            },
            {
                "name": "Potential Duplicate Transactions",
                "category": "finance", "severity": "critical",
                "check_function": "run_check_duplicate_transactions",
                "description": "Detects transactions with the same member, amount, and date — possible duplicates.",
                "run_schedule": "daily",
            },
        ]
        count = 0
        for c in checks:
            _, created = AuditCheck.objects.get_or_create(
                check_function=c["check_function"],
                defaults=c
            )
            if created:
                count += 1
        self.stdout.write(f"  ✓ {count} audit checks created")

    def setup_message_templates(self):
        from apps.communication.models import MessageTemplate, MessageChannel
        templates = [
            {
                "name": "Birthday Greeting (Email)",
                "channel": MessageChannel.EMAIL,
                "event_type": "BIRTHDAY",
                "subject": "Happy Birthday, {{first_name}}! 🎂",
                "body": "<p>Dear {{first_name}},</p><p>On behalf of the entire {{church_name}} family, we wish you a very <strong>Happy Birthday</strong>! 🎂🎉</p><p>May God bless you abundantly on your special day and throughout the year ahead.</p><p>With love,<br>{{church_name}}</p>",
                "is_html": True,
                "is_default": True,
            },
            {
                "name": "Birthday Greeting (SMS)",
                "channel": MessageChannel.SMS,
                "event_type": "BIRTHDAY",
                "subject": "",
                "body": "Happy Birthday {{first_name}}! 🎂 Wishing you God's abundant blessings on your special day. — {{church_name}}",
                "is_html": False,
                "is_default": True,
            },
            {
                "name": "Welcome New Member (Email)",
                "channel": MessageChannel.EMAIL,
                "event_type": "WELCOME",
                "subject": "Welcome to {{church_name}}, {{first_name}}!",
                "body": "<p>Dear {{first_name}},</p><p>Welcome to the <strong>{{church_name}}</strong> family! We are so glad you are here.</p><p>We look forward to growing together in faith and fellowship.</p><p>God bless you,<br>{{church_name}} Team</p>",
                "is_html": True,
                "is_default": True,
            },
            {
                "name": "Payment Receipt (SMS)",
                "channel": MessageChannel.SMS,
                "event_type": "RECEIPT",
                "subject": "",
                "body": "Dear {{first_name}}, your {{transaction_type}} of {{currency_symbol}}{{amount}} has been received. Receipt No: {{receipt_number}}. God bless you. — {{church_name}}",
                "is_html": False,
                "is_default": True,
            },
        ]
        count = 0
        for t in templates:
            _, created = MessageTemplate.objects.get_or_create(
                name=t["name"],
                defaults=t
            )
            if created:
                count += 1
        self.stdout.write(f"  ✓ {count} message templates created")
