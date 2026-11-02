from django.db import models
from apps.core.models import BaseModel


class Room(BaseModel):
    name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=50, choices=[
        ("sanctuary", "Sanctuary"), ("hall", "Hall"), ("office", "Office"),
        ("classroom", "Classroom"), ("kitchen", "Kitchen"), ("other", "Other"),
    ], default="hall")
    capacity = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    amenities = models.JSONField(default=list, blank=True)
    floor_number = models.SmallIntegerField(default=0)
    is_bookable = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RoomBooking(BaseModel):
    STATUS = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("cancelled", "Cancelled")]
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    title = models.CharField(max_length=300)
    booked_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="room_bookings")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    purpose = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_bookings")
    event = models.ForeignKey("events.Event", on_delete=models.SET_NULL, null=True, blank=True, related_name="room_bookings")

    class Meta:
        ordering = ["-start_datetime"]

    def __str__(self):
        return f"{self.room.name} — {self.title}"


class MaintenanceRequest(BaseModel):
    PRIORITY = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")]
    STATUS = [("open", "Open"), ("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")]

    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="maintenance_requests")
    title = models.CharField(max_length=300)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY, default="medium")
    status = models.CharField(max_length=20, choices=STATUS, default="open")
    reported_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="reported_maintenance")
    assigned_to = models.ForeignKey("workers.Worker", on_delete=models.SET_NULL, null=True, blank=True, related_name="maintenance_tasks")
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
