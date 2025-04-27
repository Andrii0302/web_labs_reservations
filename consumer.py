import django
import os
import pika
import json
from datetime import datetime
from dotenv import load_dotenv
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_reservations.settings')
django.setup()
 
from booking_rooms.models import AvailableSlot
from booking_rooms.models import Booking
from django.contrib.auth.models import User
load_dotenv()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE')

def callback(ch, method, properties, body):
    print("Received message:", body)
    data = json.loads(body)
    room_id = data['room_id']
    start_time = datetime.fromisoformat(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time'])
    user_id = User.objects.get(id=data['user'])

    try:
        
        slot = AvailableSlot.objects.get(
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )
        
        slot.is_available = False
        
        booking = Booking.objects.create(
            user_id=user_id.id,
            room=slot.room,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status="confirmed"
        )
        slot.save()
        print(f"Slot {slot.id} booked successfully.")
    except AvailableSlot.DoesNotExist:
        print("No available slot found or already booked.")

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE)
 
channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)

print('Waiting for booking messages...')
channel.start_consuming()