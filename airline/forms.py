from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Flight, Airplane, Passenger
from django.utils import timezone
import datetime

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

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
            'duration': forms.TextInput(attrs={'placeholder': 'HH:MM:SS'}),
        }

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'document_number', 'email', 'phone', 'date_of_birth', 'document_type']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
