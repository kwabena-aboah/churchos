from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import Speaker, SermonSeries, Sermon
from .serializers import SpeakerSerializer, SermonSeriesSerializer, SermonListSerializer, SermonDetailSerializer
from apps.core.permissions import IsAdminOrReadOnly
import logging

logger = logging.getLogger(__name__)


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

    @action(detail=True, methods=["post"], url_path="generate-summary")
    def generate_summary(self, request, pk=None):
        """Use Claude API to generate AI summary and key points from transcript."""
        sermon = self.get_object()
        if not sermon.transcript:
            return Response({"error": "No transcript available. Upload audio first."}, status=400)

        if not settings.ANTHROPIC_API_KEY:
            return Response({"error": "AI features not configured."}, status=503)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this church sermon transcript and return a JSON object with:
- "summary": 2-3 paragraph summary of the sermon
- "key_points": list of 5-7 key points/takeaways
- "scriptures": list of all Bible references mentioned

Sermon title: {sermon.title}
Transcript:
{sermon.transcript[:8000]}

Return ONLY valid JSON, no markdown."""
                }]
            )
            import json
            text = message.content[0].text.strip()
            data = json.loads(text)
            sermon.ai_summary = data.get("summary", "")
            sermon.ai_key_points = data.get("key_points", [])
            sermon.ai_scriptures_extracted = data.get("scriptures", [])
            sermon.save(update_fields=["ai_summary", "ai_key_points", "ai_scriptures_extracted"])
            return Response({"summary": sermon.ai_summary, "key_points": sermon.ai_key_points, "scriptures": sermon.ai_scriptures_extracted})
        except Exception as e:
            logger.error(f"AI sermon summary error: {e}")
            return Response({"error": "AI processing failed."}, status=500)

    @action(detail=True, methods=["post"], url_path="transcribe")
    def transcribe(self, request, pk=None):
        """Transcribe audio using OpenAI Whisper."""
        sermon = self.get_object()
        if not sermon.audio_file:
            return Response({"error": "No audio file attached."}, status=400)
        if not settings.OPENAI_API_KEY:
            return Response({"error": "OpenAI not configured."}, status=503)
        try:
            import openai
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            with sermon.audio_file.open("rb") as audio:
                transcript_resp = client.audio.transcriptions.create(model="whisper-1", file=audio)
            sermon.transcript = transcript_resp.text
            from django.utils import timezone
            sermon.transcript_generated_at = timezone.now()
            sermon.save(update_fields=["transcript", "transcript_generated_at"])
            return Response({"transcript": sermon.transcript})
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return Response({"error": "Transcription failed."}, status=500)
