import uuid
from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    capacity = models.IntegerField(default=0, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AvailableSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="available_slots", blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room.name} | {self.start_time} - {self.end_time}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("canceled", "Canceled"),
        ("pending", "Pending"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.room.name} ({self.start_time} - {self.end_time})"

