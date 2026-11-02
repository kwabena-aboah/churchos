from django.contrib.auth import get_user_model
from django.db import connection
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.constants import Role
from .fields import EncryptedCharField
from .models import ChurchSettings


class HealthCheckTests(SimpleTestCase):
    def test_health_check_is_available_without_authentication(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class EncryptedCharFieldTests(SimpleTestCase):
    def test_round_trips_encrypted_value(self):
        field = EncryptedCharField(max_length=1024)
        secret = "test-api-key"

        encrypted = field.get_prep_value(secret)

        self.assertNotEqual(encrypted, secret)
        self.assertTrue(encrypted.startswith(field.prefix))
        self.assertEqual(field.from_db_value(encrypted, None, None), secret)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "core-ai-settings-tests",
        }
    }
)
class AISettingsAndChatTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email="ai-test@example.com",
            password="test-password",
            first_name="AI",
            last_name="Tester",
            role=Role.ADMINISTRATOR,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.church = ChurchSettings.load()

    def test_ai_keys_are_encrypted_and_not_returned_by_settings_api(self):
        response = self.client.patch(
            "/api/v1/core/settings/",
            {
                "ai_anthropic_api_key": "anthropic-test-key",
                "ai_provider": "anthropic",
            },
            format="multipart",
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ai_anthropic_api_key FROM core_churchsettings WHERE id = 1"
            )
            stored_value = cursor.fetchone()[0]

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(stored_value, "anthropic-test-key")
        self.assertTrue(stored_value.startswith("fernet:v1:"))
        self.assertNotIn("ai_anthropic_api_key", response.data)
        self.assertTrue(response.data["has_ai_anthropic_api_key"])

        clear_response = self.client.patch(
            "/api/v1/core/settings/",
            {"clear_ai_anthropic_api_key": "true"},
            format="multipart",
        )
        self.church.refresh_from_db()

        self.assertEqual(clear_response.status_code, 200)
        self.assertEqual(self.church.ai_anthropic_api_key, "")

    def test_existing_logo_url_is_not_required_for_settings_update(self):
        response = self.client.patch(
            "/api/v1/core/settings/",
            {"church_name": "Updated Church", "logo_url": "/media/church/logo.png"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["church_name"], "Updated Church")

    @override_settings(ANTHROPIC_API_KEY="", OPENAI_API_KEY="")
    def test_builtin_assistant_responds_without_api_keys(self):
        self.church.enable_ai_features = True
        self.church.ai_provider = "auto"
        self.church.save()

        response = self.client.post(
            "/api/v1/core/assistant/chat/",
            {"messages": [{"role": "user", "content": "How many members do we have?"}]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["provider"], "built_in")
        self.assertIn("active members", response.data["reply"])

    def test_chat_is_disabled_when_ai_features_are_off(self):
        response = self.client.post(
            "/api/v1/core/assistant/chat/",
            {"messages": [{"role": "user", "content": "Hello"}]},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
