from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Booking, Passenger

# Formulario para la creación y edición de pasajeros.
class PassengerForm(forms.ModelForm):
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
    class Meta:
        model = Booking
        # Campos del modelo Booking que se incluirán en el formulario.
        fields = ['flight', 'passenger', 'seat']

    # Método de limpieza para el campo 'seat'.
    def clean_seat(self):
        seat = self.cleaned_data['seat']
        # Valida que el asiento seleccionado esté disponible.
        if seat.status != 'available':
            raise forms.ValidationError(_("This seat is not available."))
        return seat
