from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Booking, Passenger

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'document_id', 'email', 'phone']
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'document_id': _('Document ID'),
            'email': _('Email'),
            'phone': _('Phone'),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['flight', 'passenger', 'seat']

    def clean_seat(self):
        seat = self.cleaned_data['seat']
        if seat.status != 'available':
            raise forms.ValidationError(_("This seat is not available."))
        return seat
