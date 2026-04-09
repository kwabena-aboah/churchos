from django.db import models
from apps.core.models import BaseModel


class DiscipleshipTrack(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    duration_weeks = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class DiscipleshipClass(BaseModel):
    track = models.ForeignKey(DiscipleshipTrack, on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=200)
    facilitator = models.ForeignKey("workers.Worker", on_delete=models.SET_NULL, null=True, blank=True, related_name="facilitated_classes")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.track.name} — {self.name}"


class DiscipleshipEnrollment(BaseModel):
    STATUS = [("enrolled", "Enrolled"), ("active", "Active"), ("completed", "Completed"), ("dropped", "Dropped")]
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, related_name="discipleship_enrollments")
    discipleship_class = models.ForeignKey(DiscipleshipClass, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS, default="enrolled")
    enrolled_at = models.DateField(auto_now_add=True)
    completed_at = models.DateField(null=True, blank=True)
    attendance_count = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        unique_together = [["member", "discipleship_class"]]
        ordering = ["-enrolled_at"]
