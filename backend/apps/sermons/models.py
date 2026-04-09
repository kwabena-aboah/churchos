from django.db import models
from auditlog.registry import auditlog
from apps.core.models import BaseModel, ServiceType


class Speaker(BaseModel):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=100, blank=True)  # Pastor, Rev, Dr, etc.
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="sermons/speakers/", null=True, blank=True)
    email = models.EmailField(blank=True)
    is_external = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} {self.name}".strip()


class SermonSeries(BaseModel):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    artwork = models.ImageField(upload_to="sermons/series/", null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Sermon Series"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    @property
    def sermon_count(self):
        return self.sermons.count()


class Sermon(BaseModel):
    title = models.CharField(max_length=400)
    series = models.ForeignKey(SermonSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="sermons")
    speaker = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True, blank=True, related_name="sermons")
    service_type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()

    # Scripture references
    primary_scripture = models.CharField(max_length=200, blank=True, help_text="e.g. John 3:16")
    secondary_scriptures = models.TextField(blank=True, help_text="Other references, comma-separated")

    # Topics & tags
    topics = models.JSONField(default=list, blank=True, help_text="List of topic strings")

    # Content
    notes_pdf = models.FileField(upload_to="sermons/notes/", null=True, blank=True)
    audio_file = models.FileField(upload_to="sermons/audio/", null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    description = models.TextField(blank=True)

    # AI-generated content
    transcript = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    ai_key_points = models.JSONField(default=list, blank=True)
    ai_scriptures_extracted = models.JSONField(default=list, blank=True)
    transcript_generated_at = models.DateTimeField(null=True, blank=True)

    # Visibility
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["date"]), models.Index(fields=["speaker"])]

    def __str__(self):
        return f"{self.title} — {self.date}"


auditlog.register(Sermon)
