from django.db import migrations


def make_changes_text_nullable(apps, schema_editor):
    log_entry = apps.get_model("auditlog", "LogEntry")
    old_field = log_entry._meta.get_field("changes_text")
    new_field = old_field.clone()
    new_field.null = True
    new_field.set_attributes_from_name(old_field.name)
    new_field.model = log_entry

    schema_editor.alter_field(log_entry, old_field, new_field)


class Migration(migrations.Migration):
    dependencies = [
        ("auditlog", "0015_alter_logentry_changes"),
        ("finance", "0001_initial"),
    ]

    operations = [
        # Keep this as a database-only change; auditlog's model remains unchanged.
        migrations.RunPython(make_changes_text_nullable),
    ]
