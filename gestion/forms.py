from django import forms
from .models import Reserva, Pasajero

class PasajeroForm(forms.ModelForm):
    class Meta:
        model = Pasajero
        fields = ['nombre', 'apellido', 'documento', 'email', 'telefono']

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['vuelo', 'pasajero', 'asiento']

    def clean_asiento(self):
        asiento = self.cleaned_data['asiento']
        if asiento.estado != 'disponible':
            raise forms.ValidationError("Este asiento no está disponible.")
        return asiento
