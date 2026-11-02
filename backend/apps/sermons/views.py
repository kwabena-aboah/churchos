from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from apps.core.ai import DEFAULT_MODELS, get_ai_api_key, get_configured_provider
from apps.core.models import ChurchSettings
from .models import Speaker, SermonSeries, Sermon
from .serializers import SpeakerSerializer, SermonSeriesSerializer, SermonListSerializer, SermonDetailSerializer
from apps.core.permissions import IsAdminOrReadOnly
import json
import logging

import anthropic
import openai

logger = logging.getLogger(__name__)

MAX_TRANSCRIPTION_FILE_SIZE = 25 * 1024 * 1024


class SpeakerViewSet(viewsets.ModelViewSet):
    queryset = Speaker.objects.filter(is_active=True)
    serializer_class = SpeakerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["name", "title"]


class SermonSeriesViewSet(viewsets.ModelViewSet):
    queryset = SermonSeries.objects.filter(is_active=True)
    serializer_class = SermonSeriesSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["title", "description"]
    filterset_fields = ["is_complete"]


class SermonViewSet(viewsets.ModelViewSet):
    queryset = Sermon.objects.filter(is_active=True).select_related("speaker", "series", "service_type")
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["title", "primary_scripture", "description", "transcript"]
    filterset_fields = ["series", "speaker", "service_type", "is_public"]
    ordering_fields = ["date", "title"]

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return SermonDetailSerializer
        return SermonListSerializer

    @action(
        detail=True,
        methods=["post"],
        url_path="generate-summary",
        permission_classes=[IsAuthenticated],
    )
    def generate_summary(self, request, pk=None):
        """Generate and save a summary using the configured AI provider."""
        sermon = self.get_object()
        church = ChurchSettings.get_cached()
        if not church.enable_ai_features:
            return Response(
                {"detail": "Enable AI features in System Settings to use sermon tools."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not sermon.transcript:
            return Response(
                {"detail": "Add a transcript or transcribe audio before generating a summary."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        provider = get_configured_provider(church)
        if provider == "built_in":
            return Response(
                {
                    "detail": (
                        "Sermon summaries require an Anthropic or OpenAI API key. "
                        "Add one in Settings → Integrations & AI."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            prompt = f"""Analyze this church sermon transcript and return a JSON object with:
- "summary": 2-3 paragraph summary of the sermon
- "key_points": list of 5-7 key points/takeaways
- "scriptures": list of all Bible references mentioned

Sermon title: {sermon.title}
Transcript:
{sermon.transcript[:8000]}

Return ONLY valid JSON, no markdown."""
            if provider == "anthropic":
                message = anthropic.Anthropic(
                    api_key=get_ai_api_key("anthropic", church)
                ).messages.create(
                    model=church.ai_anthropic_model or DEFAULT_MODELS["anthropic"],
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = message.content[0].text.strip()
            else:
                completion = openai.OpenAI(
                    api_key=get_ai_api_key("openai", church)
                ).chat.completions.create(
                    model=church.ai_openai_model or DEFAULT_MODELS["openai"],
                    max_tokens=1500,
                    response_format={"type": "json_object"},
                    messages=[
                        {
                            "role": "system",
                            "content": "Return a JSON object with summary, key_points, and scriptures.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
                text = completion.choices[0].message.content.strip()
            data = json.loads(text)
            summary = data.get("summary")
            key_points = data.get("key_points", [])
            scriptures = data.get("scriptures", [])
            if not isinstance(summary, str) or not summary.strip():
                raise ValueError("AI response did not contain a valid summary.")
            if not isinstance(key_points, list) or not isinstance(scriptures, list):
                raise ValueError("AI response did not contain valid summary details.")

            sermon.ai_summary = summary
            sermon.ai_key_points = key_points
            sermon.ai_scriptures_extracted = scriptures
            sermon.save(update_fields=["ai_summary", "ai_key_points", "ai_scriptures_extracted"])
            return Response({
                "ai_summary": sermon.ai_summary,
                "ai_key_points": sermon.ai_key_points,
                "ai_scriptures_extracted": sermon.ai_scriptures_extracted,
            })
        except (anthropic.APIError, openai.APIError, ValueError):
            logger.exception("AI sermon summary failed for sermon %s", sermon.pk)
            return Response(
                {"detail": "AI summary generation failed. Check the provider settings and try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="transcribe",
        permission_classes=[IsAuthenticated],
    )
    def transcribe(self, request, pk=None):
        """Transcribe audio using OpenAI Whisper."""
        sermon = self.get_object()
        church = ChurchSettings.get_cached()
        if not church.enable_ai_features:
            return Response(
                {"detail": "Enable AI features in System Settings to use sermon tools."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not sermon.audio_file:
            return Response(
                {"detail": "Upload an audio file before requesting transcription."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if sermon.audio_file.size > MAX_TRANSCRIPTION_FILE_SIZE:
            return Response(
                {"detail": "Audio files must be 25 MB or smaller for transcription."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        api_key = get_ai_api_key("openai", church)
        if not api_key:
            return Response(
                {
                    "detail": (
                        "Audio transcription requires an OpenAI API key. "
                        "Add one in Settings → Integrations & AI."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        try:
            client = openai.OpenAI(api_key=api_key)
            with sermon.audio_file.open("rb") as audio:
                transcript_resp = client.audio.transcriptions.create(model="whisper-1", file=audio)
            sermon.transcript = transcript_resp.text
            from django.utils import timezone
            sermon.transcript_generated_at = timezone.now()
            sermon.save(update_fields=["transcript", "transcript_generated_at"])
            return Response({"transcript": sermon.transcript})
        except openai.APIError:
            logger.exception("Sermon transcription failed for sermon %s", sermon.pk)
            return Response(
                {"detail": "Audio transcription failed. Check the OpenAI API settings and try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="upload-audio",
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_audio(self, request, pk=None):
        sermon = self.get_object()
        church = ChurchSettings.get_cached()
        if not church.enable_ai_features:
            return Response(
                {"detail": "Enable AI features in System Settings to upload audio for AI tools."},
                status=status.HTTP_403_FORBIDDEN,
            )

        audio_file = request.FILES.get("audio_file")
        if audio_file is None:
            return Response(
                {"detail": "Select an audio file to upload."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if audio_file.size > MAX_TRANSCRIPTION_FILE_SIZE:
            return Response(
                {"detail": "Audio files must be 25 MB or smaller for transcription."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (audio_file.content_type or "").startswith("audio/"):
            return Response(
                {"detail": "Choose a valid audio file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sermon.audio_file = audio_file
        sermon.save(update_fields=["audio_file", "updated_at"])
        return Response({"audio_file": sermon.audio_file.url})
