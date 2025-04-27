from django.urls import path
from .views import CreateRoomView,CreateAvailableSlotView,RoomAvailableSlotsView,BookingView

urlpatterns = [
    path('rooms/', CreateRoomView.as_view(), name='create-room'),
    path('rooms/<uuid:room_id>/', CreateRoomView.as_view(), name='edit-room'),
    path('rooms/<uuid:room_id>/slots/', RoomAvailableSlotsView.as_view(), name='room-available-slots'),
    path('create-available-slot/', CreateAvailableSlotView.as_view(), name='create-available-slot'),
    path('bookings/', BookingView.as_view(), name='create-booking'),
    path('bookings/<int:user_id>/', BookingView.as_view(), name='bookings-details'),
    path('bookings/<uuid:booking_id>/', BookingView.as_view(), name='cancel-booking'),
]