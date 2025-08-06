from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Booking

@receiver(post_delete, sender=Booking)
def update_seat_status(sender, instance, **kwargs):
    seat = instance.seat
    seat.status = 'available'
    seat.save()
