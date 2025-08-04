from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Reserva

@receiver(post_delete, sender=Reserva)
def actualizar_estado_asiento(sender, instance, **kwargs):
    asiento = instance.asiento
    asiento.estado = 'disponible'
    asiento.save()
