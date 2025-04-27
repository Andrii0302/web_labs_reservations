from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RoomSerializer, AvailableSlotSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Room,AvailableSlot
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
import pika
import json
from .config import RABBITMQ_HOST, RABBITMQ_QUEUE
from .models import Booking

class CreateAvailableSlotView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        
        if not request.user.is_staff:
            return Response(
                {"message": "You do not have permission to create an available slot."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AvailableSlotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Available slot created successfully.", "body": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CreateRoomView(APIView):
    permission_classes = [IsAuthenticated] 
    
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"message": "You do not have permission to create a room."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Room created successfully.", "body": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        available_rooms = Room.objects.filter(available_slots__is_available=True).distinct()
        serializer = RoomSerializer(available_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response(
                {"message": "Room not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_staff:
            return Response(
                {"message": "You do not have permission to edit this room."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Room updated successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomAvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response(
                {"message": "Room not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        available_slots = room.available_slots.filter(is_available=True)
        serializer = AvailableSlotSerializer(available_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE)
            message = {
                'room_id':data['room'],
                'start_time':data['start_time'],
                'end_time':data['end_time'],
                'user':data['user']
            }
            channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=json.dumps(message))
            connection.close()
            return Response(
                {"message": "Availability check request sent.", "body": serializer.data},
                status=status.HTTP_202_ACCEPTED
            )
        return Response({"message":"Slot is not available"}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, user_id):

        bookings = Booking.objects.filter(user_id=user_id)
        if not bookings.exists():
            return Response(
                {"message": "No bookings found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            if booking.user != request.user:
                return Response(
                    {"message": "You do not have permission to cancel this booking."},
                    status=status.HTTP_403_FORBIDDEN
                )
            booking.status = "canceled"
            booking.save()

            return Response(
                {"message": f"Booking {booking_id} has been canceled."},
                status=status.HTTP_200_OK
            )
        except Booking.DoesNotExist:
            return Response(
                {"message": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )