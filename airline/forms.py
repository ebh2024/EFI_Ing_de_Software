from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Flight, Airplane, Passenger, Seat, Reservation, Ticket, SeatLayout, SeatType, SeatLayoutPosition
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import datetime
import uuid

def add_bootstrap_classes(form):
    for field_name, field in form.fields.items():
        if not isinstance(field.widget, (forms.HiddenInput, forms.CheckboxInput, forms.RadioSelect)):
            attrs = field.widget.attrs
            attrs['class'] = attrs.get('class', '') + ' form-control'
            if field_name in ['departure_date', 'arrival_date']: # Use field_name here
                attrs['class'] += ' datetime-input' # Add a specific class for datetime inputs if needed
            field.widget.attrs = attrs
    return form

class AirplaneForm(forms.ModelForm):
    class Meta:
        model = Airplane
        fields = ['model_name', 'manufacturer', 'registration_number', 'year_of_manufacture', 'capacity', 'seat_layout', 'last_maintenance_date', 'technical_notes']
        widgets = {
            'model_name': forms.TextInput(attrs={'required': 'true'}),
            'registration_number': forms.TextInput(attrs={'required': 'true'}),
            'year_of_manufacture': forms.NumberInput(attrs={'min': '1900'}),
            'capacity': forms.NumberInput(attrs={'min': '1'}),
            'last_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'technical_notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean(self):
        cleaned_data = super().clean()
        # Model-level validation will be handled when the instance is saved in the view.
        # For forms, we primarily validate the fields present in the form.
        return cleaned_data

class SeatLayoutForm(forms.ModelForm):
    class Meta:
        model = SeatLayout
        fields = ['layout_name', 'rows', 'columns']
        widgets = {
            'layout_name': forms.TextInput(attrs={'required': 'true'}),
            'rows': forms.NumberInput(attrs={'min': '1'}),
            'columns': forms.NumberInput(attrs={'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean(self):
        cleaned_data = super().clean()
        # Model-level validation will be handled when the instance is saved in the view.
        return cleaned_data

class SeatTypeForm(forms.ModelForm):
    class Meta:
        model = SeatType
        fields = ['name', 'code', 'price_multiplier']
        widgets = {
            'name': forms.TextInput(attrs={'required': 'true'}),
            'code': forms.TextInput(attrs={'required': 'true'}),
            'price_multiplier': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean(self):
        cleaned_data = super().clean()
        # Model-level validation will be handled when the instance is saved in the view.
        return cleaned_data

class SeatLayoutPositionForm(forms.ModelForm):
    class Meta:
        model = SeatLayoutPosition
        fields = ['seat_layout', 'seat_type', 'row', 'column']
        widgets = {
            'row': forms.NumberInput(attrs={'min': '1'}),
            'column': forms.TextInput(attrs={'required': 'true', 'maxlength': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean(self):
        cleaned_data = super().clean()
        # Model-level validation will be handled when the instance is saved in the view.
        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_("Email"))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("This email address is already in use."))
        return email

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

class FlightForm(forms.ModelForm):
    departure_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    arrival_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Flight
        fields = ['airplane', 'origin', 'destination', 'departure_date', 'arrival_date', 'duration', 'status', 'base_price']
        widgets = {
            'origin': forms.TextInput(attrs={'required': 'true'}),
            'destination': forms.TextInput(attrs={'required': 'true'}),
            'base_price': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'duration': forms.TextInput(attrs={'placeholder': 'HH:MM:SS', 'required': 'true'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_duration(self):
        duration_data = self.cleaned_data.get('duration')
        if isinstance(duration_data, datetime.timedelta):
            return duration_data
        
        if duration_data:
            try:
                # Attempt to parse duration in HH:MM:SS format
                h, m, s = map(int, duration_data.split(':'))
                duration = datetime.timedelta(hours=h, minutes=m, seconds=s)
                return duration
            except ValueError:
                raise forms.ValidationError("Duration must be in HH:MM:SS format.")
        return duration_data

    def clean(self):
        cleaned_data = super().clean()
        # Model-level validation will be handled when the instance is saved in the view.
        return cleaned_data

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'document_number', 'email', 'phone', 'date_of_birth', 'document_type']
        widgets = {
            'first_name': forms.TextInput(attrs={'required': 'true'}),
            'document_number': forms.TextInput(attrs={'required': 'true'}),
            'email': forms.EmailInput(attrs={'required': 'true'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'max': timezone.now().strftime('%Y-%m-%d')}),
            'phone': forms.TextInput(attrs={'pattern': '[0-9]{7,15}', 'title': 'Phone number must be 7-15 digits'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean(self):
        cleaned_data = super().clean()
        # Model-level validation will be handled when the instance is saved in the view.
        return cleaned_data

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['flight', 'seat', 'status', 'price'] # Removed 'passenger' as it's set by the view
        widgets = {
            'status': forms.HiddenInput(), # Status will be set by the view
            'price': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}), # Price will be calculated by the view, but ensure it's positive if manually set
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally, filter seats based on the selected flight if flight is already known
        if 'flight' in self.initial:
            self.fields['seat'].queryset = Seat.objects.filter(airplane=self.initial['flight'].airplane, status='Available')
        else:
            self.fields['seat'].queryset = Seat.objects.none() # No seats initially
        add_bootstrap_classes(self)

    def clean(self):
        cleaned_data = super().clean()
        # Model-level validation will be handled when the instance is saved in the view.
        return cleaned_data

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['reservation', 'barcode', 'status']
        widgets = {
            'barcode': forms.HiddenInput(), # Barcode will be generated by the view
            'status': forms.HiddenInput(),  # Status will be set by the view
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk: # Only generate barcode for new tickets
            self.initial['barcode'] = str(uuid.uuid4()).replace('-', '')[:20] # Generate a unique barcode
        self.fields['reservation'].queryset = Reservation.objects.filter(status='CON') # Only allow confirmed reservations
        add_bootstrap_classes(self)

    def clean(self):
        cleaned_data = super().clean()
        # Model-level validation will be handled when the instance is saved in the view.
        return cleaned_data
