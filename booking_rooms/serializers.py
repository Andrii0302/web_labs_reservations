from .models import Room, AvailableSlot,Booking
from rest_framework import serializers
    
class AvailableSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableSlot
        fields = ['id', 'room', 'start_time', 'end_time', 'is_available']

    def create(self, validated_data):
        return AvailableSlot.objects.create(**validated_data)
class RoomSerializer(serializers.ModelSerializer):
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'location', 'capacity', 'type', 'description', 'available_slots']

    def get_available_slots(self, obj):
        # Only include slots where is_available=True
        slots = obj.available_slots.filter(is_available=True)
        return AvailableSlotSerializer(slots, many=True).data
    
class RoomSerializer(serializers.ModelSerializer):
    available_slots = AvailableSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'location', 'capacity', 'type', 'description', 'available_slots']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'room', 'start_time', 'end_time', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")

        overlapping_bookings = Booking.objects.filter(
            room=data['room'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time'],
            status="confirmed"
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError("The room is not available during the requested time.")

        return data

    def create(self, validated_data):
        validated_data['status'] = "pending"
        return super().create(validated_data)
