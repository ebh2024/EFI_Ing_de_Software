import logging

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Booking, Passenger

logger = logging.getLogger('gestion')

# Formulario para la creación y edición de pasajeros.
class PassengerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("PassengerForm initialized.")

    class Meta:
        model = Passenger
        # Campos del modelo Passenger que se incluirán en el formulario.
        fields = ['first_name', 'last_name', 'document_id', 'email', 'phone']
        # Etiquetas personalizadas para los campos del formulario.
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'document_id': _('Document ID'),
            'email': _('Email'),
            'phone': _('Phone'),
        }

# Formulario para la creación de reservas (aunque la lógica de reserva se maneja más en services.py).
class BookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("BookingForm initialized.")

    class Meta:
        model = Booking
        # Campos del modelo Booking que se incluirán en el formulario.
        fields = ['flight', 'passenger', 'seat']

    # Método de limpieza para el campo 'seat'.
    def clean_seat(self):
        seat = self.cleaned_data['seat']
        logger.info(f"Validating seat {seat.id} for availability. Current status: {seat.status}")
        # Valida que el asiento seleccionado esté disponible.
        if seat.status != 'available':
            logger.warning(f"Seat {seat.id} is not available. Status: {seat.status}")
            raise forms.ValidationError(_("This seat is not available."))
        logger.info(f"Seat {seat.id} is available.")
        return seat
