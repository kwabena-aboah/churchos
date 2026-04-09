from rest_framework import serializers
from .models import Speaker, SermonSeries, Sermon


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = "__all__"


class SermonSeriesSerializer(serializers.ModelSerializer):
    sermon_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SermonSeries
        fields = "__all__"


class SermonListSerializer(serializers.ModelSerializer):
    speaker_name = serializers.CharField(source="speaker.__str__", read_only=True)
    series_title = serializers.CharField(source="series.title", read_only=True)
    has_audio = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    has_notes = serializers.SerializerMethodField()

    class Meta:
        model = Sermon
        fields = [
            "id", "title", "date", "speaker", "speaker_name", "series", "series_title",
            "primary_scripture", "topics", "description", "is_public",
            "has_audio", "has_video", "has_notes", "created_at",
        ]

    def get_has_audio(self, obj):
        return bool(obj.audio_file)

    def get_has_video(self, obj):
        return bool(obj.video_url)

    def get_has_notes(self, obj):
        return bool(obj.notes_pdf)


class SermonDetailSerializer(serializers.ModelSerializer):
    speaker_detail = SpeakerSerializer(source="speaker", read_only=True)
    series_detail = SermonSeriesSerializer(source="series", read_only=True)
    has_transcript = serializers.SerializerMethodField()

    class Meta:
        model = Sermon
        fields = "__all__"

    def get_has_transcript(self, obj):
        return bool(obj.transcript)
