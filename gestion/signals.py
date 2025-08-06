from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Booking, Flight
from .services import NotificationService # Import the NotificationService

@receiver(post_delete, sender=Booking)
def update_seat_status(sender, instance, **kwargs):
    seat = instance.seat
    seat.status = 'available'
    seat.save()

# This signal is now handled in services.py to keep related logic together.
# @receiver(post_save, sender=Flight)
# def flight_update_notification(sender, instance, created, **kwargs):
#     if not created:
#         notification_service = NotificationService()
#         bookings = instance.booking_set.all()
#         for booking in bookings:
#             message = f"Update for your flight {instance.origin} to {instance.destination} on {instance.departure_date.strftime('%d/%m/%Y %H:%M')}. Please check flight details."
#             notification_service.create_notification(booking.passenger.user, message, instance)
