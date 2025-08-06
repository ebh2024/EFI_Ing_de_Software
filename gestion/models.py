from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class Aircraft(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.IntegerField()
    seat_layout = models.JSONField(default=dict)
    technical_information = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.model

class Flight(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.origin} to {self.destination}"

    def clean(self):
        if self.arrival_date <= self.departure_date:
            raise ValidationError(_('Arrival date must be after departure date.'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        if self.aircraft and not Seat.objects.filter(flight=self).exists():
            layout = self.aircraft.seat_layout
            for row in layout.get('rows', []):
                for seat_info in row.get('seats', []):
                    Seat.objects.create(flight=self, number=seat_info['number'])

class Passenger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document_id = models.CharField(max_length=20, null=True, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def flight_history(self):
        return self.booking_set.all()

class Seat(models.Model):
    STATUS_CHOICES = (
        ('available', _('Available')),
        ('reserved', _('Reserved')),
        ('occupied', _('Occupied')),
    )
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return _("Seat %(number)s on flight %(flight)s") % {'number': self.number, 'flight': self.flight}

class Booking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, null=True)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return _("Booking for %(passenger)s on flight %(flight)s, seat %(seat)s") % {'passenger': self.passenger, 'flight': self.flight, 'seat': self.seat.number}
