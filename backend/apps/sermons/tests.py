import json
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.constants import Role
from apps.core.models import ChurchSettings
from .models import Sermon


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "sermon-ai-tests",
        }
    }
)
class SermonAITests(TestCase):
    def setUp(self):
        cache.clear()
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        override = override_settings(MEDIA_ROOT=self.media_dir.name)
        override.enable()
        self.addCleanup(override.disable)

        user = get_user_model().objects.create_user(
            email="sermon-ai@example.com",
            password="test-password",
            first_name="Sermon",
            last_name="User",
            role=Role.DATA_ENTRY,
        )
        self.client = APIClient()
        self.client.force_authenticate(user)

        ChurchSettings.objects.all().delete()
        self.church = ChurchSettings.load()
        self.sermon = Sermon.objects.create(
            title="Test Sermon",
            date="2026-11-02",
            transcript="A test transcript about hope and service.",
        )

    def test_summary_is_blocked_when_ai_is_disabled(self):
        response = self.client.post(
            f"/api/v1/sermons/{self.sermon.pk}/generate-summary/"
        )

        self.assertEqual(response.status_code, 403)

    def test_summary_requires_a_configured_ai_provider(self):
        self.church.enable_ai_features = True
        self.church.save()

        with patch("apps.sermons.views.get_configured_provider", return_value="built_in"):
            response = self.client.post(
                f"/api/v1/sermons/{self.sermon.pk}/generate-summary/"
            )

        self.assertEqual(response.status_code, 503)

    def test_summary_uses_configured_provider_and_returns_saved_fields(self):
        self.church.enable_ai_features = True
        self.church.ai_provider = "anthropic"
        self.church.ai_anthropic_api_key = "test-anthropic-key"
        self.church.save()
        provider_response = SimpleNamespace(
            content=[
                SimpleNamespace(
                    text=json.dumps({
                        "summary": "A sermon about hope.",
                        "key_points": ["Serve others"],
                        "scriptures": ["Romans 12:12"],
                    })
                )
            ]
        )

        with patch(
            "apps.sermons.views.anthropic.Anthropic"
        ) as anthropic_client:
            anthropic_client.return_value.messages.create.return_value = provider_response
            response = self.client.post(
                f"/api/v1/sermons/{self.sermon.pk}/generate-summary/"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ai_summary"], "A sermon about hope.")
        self.assertEqual(response.data["ai_key_points"], ["Serve others"])
        self.assertEqual(response.data["ai_scriptures_extracted"], ["Romans 12:12"])
        self.sermon.refresh_from_db()
        self.assertEqual(self.sermon.ai_summary, "A sermon about hope.")

    def test_audio_transcription_is_blocked_when_ai_is_disabled(self):
        self.sermon.audio_file = SimpleUploadedFile(
            "sermon.wav",
            b"audio-content",
            content_type="audio/wav",
        )
        self.sermon.save()

        response = self.client.post(
            f"/api/v1/sermons/{self.sermon.pk}/transcribe/"
        )

        self.assertEqual(response.status_code, 403)

    def test_audio_transcription_uses_configured_openai_key(self):
        self.church.enable_ai_features = True
        self.church.ai_provider = "openai"
        self.church.ai_openai_api_key = "test-openai-key"
        self.church.save()
        self.sermon.audio_file = SimpleUploadedFile(
            "sermon.wav",
            b"audio-content",
            content_type="audio/wav",
        )
        self.sermon.save()

        with patch("apps.sermons.views.openai.OpenAI") as openai_client:
            openai_client.return_value.audio.transcriptions.create.return_value.text = (
                "A transcribed sermon."
            )
            response = self.client.post(
                f"/api/v1/sermons/{self.sermon.pk}/transcribe/"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["transcript"], "A transcribed sermon.")
        self.sermon.refresh_from_db()
        self.assertEqual(self.sermon.transcript, "A transcribed sermon.")

    def test_audio_upload_requires_ai_enabled(self):
        response = self.client.post(
            f"/api/v1/sermons/{self.sermon.pk}/upload-audio/",
            {"audio_file": SimpleUploadedFile(
                "sermon.wav", b"audio-content", content_type="audio/wav"
            )},
            format="multipart",
        )

        self.assertEqual(response.status_code, 403)

    def test_audio_upload_succeeds_when_ai_is_enabled(self):
        self.church.enable_ai_features = True
        self.church.save()

        response = self.client.post(
            f"/api/v1/sermons/{self.sermon.pk}/upload-audio/",
            {"audio_file": SimpleUploadedFile(
                "sermon.wav", b"audio-content", content_type="audio/wav"
            )},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.sermon.refresh_from_db()
        self.assertTrue(self.sermon.audio_file.name.endswith("sermon.wav"))
