from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from auditlog.models import LogEntry


class AuditLogChangesTextCompatibilityTests(TestCase):
    def test_log_entry_accepts_null_changes_text(self):
        self.assertTrue(LogEntry._meta.get_field("changes_text").blank)

        entry = LogEntry.objects.create(
            content_type=ContentType.objects.get_for_model(LogEntry),
            object_pk="nullable-changes-text-test",
            object_repr="Nullable changes text test",
            action=LogEntry.Action.CREATE,
            changes_text=None,
        )

        self.assertIsNone(entry.changes_text)
