from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Airplane(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.IntegerField()
    rows = models.IntegerField()
    columns = models.IntegerField()

    def __str__(self):
        return f"{self.model} ({self.capacity} seats)"

class Flight(models.Model):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField()
    duration = models.DurationField()
    status = models.CharField(max_length=50)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Flight {self.origin} to {self.destination} on {self.departure_date.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        if self.arrival_date <= self.departure_date:
            raise ValidationError('Arrival date must be after departure date.')
        if self.departure_date < timezone.now():
            raise ValidationError('Departure date cannot be in the past.')

class Passenger(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('DNI', 'National Identity Document'),
        ('PAS', 'Passport'),
        ('LE', 'Enrollment Booklet'),
        ('LC', 'Civic Booklet'),
    ]
    first_name = models.CharField(max_length=100)
    document_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField()
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPE_CHOICES, default='DNI')

    def __str__(self):
        return self.first_name

    def clean(self):
        # Basic email validation
        if not self.email or '@' not in self.email:
            raise ValidationError('Invalid email.')
        # We could add more document validations if a format were specified

class Seat(models.Model):
    SEAT_TYPE_CHOICES = [
        ('ECO', 'Economy'),
        ('PRE', 'Premium'),
        ('EXE', 'Executive'),
    ]
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    row = models.IntegerField()
    column = models.CharField(max_length=2)
    type = models.CharField(max_length=3, choices=SEAT_TYPE_CHOICES, default='ECO')
    status = models.CharField(max_length=20) # E.g.: 'Available', 'Occupied', 'Reserved'

    def __str__(self):
        return f"Seat {self.number} - {self.airplane.model}"

class Reservation(models.Model):
    RESERVATION_STATUS_CHOICES = [
        ('PEN', 'Pending'),
        ('CON', 'Confirmed'),
        ('CAN', 'Cancelled'),
        ('PAID', 'Paid'),
    ]
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    status = models.CharField(max_length=4, choices=RESERVATION_STATUS_CHOICES, default='PEN')
    reservation_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reservation_code = models.CharField(max_length=20, unique=True)

    class Meta:
        unique_together = (('flight', 'seat'), ('flight', 'passenger'))

    def __str__(self):
        return f"Reservation {self.reservation_code} for {self.passenger.first_name} on flight {self.flight.id}"

    def clean(self):
        # Restriction: A seat cannot be reserved more than once per flight (already covered by unique_together)
        # Restriction: A passenger cannot have more than one reservation per flight (already covered by unique_together)

        # Restriction: Seat statuses must be consistent with reservations
        if self.status == 'CON' or self.status == 'PAID':
            if self.seat.status != 'Reserved' and self.seat.status != 'Occupied':
                raise ValidationError('The seat must be in "Reserved" or "Occupied" status for a confirmed/paid reservation.')
        elif self.status == 'CAN':
            if self.seat.status != 'Available':
                raise ValidationError('The seat must be in "Available" status for a cancelled reservation.')

    def save(self, *args, **kwargs):
        # Update seat status when saving the reservation
        if self.status == 'CON' or self.status == 'PAID':
            self.seat.status = 'Reserved'
        elif self.status == 'CAN':
            self.seat.status = 'Available'
        self.seat.save()
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADM', 'Administrator'),
        ('EMP', 'Employee'),
        ('CLI', 'Client'),
    ]
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128) # It is recommended to use a password hash
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=3, choices=ROLE_CHOICES, default='CLI')

    def __str__(self):
        return self.username

class Ticket(models.Model):
    TICKET_STATUS_CHOICES = [
        ('EMI', 'Issued'),
        ('CAN', 'Cancelled'),
        ('USED', 'Used'),
    ]
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=50, unique=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=4, choices=TICKET_STATUS_CHOICES, default='EMI')

    def __str__(self):
        return f"Ticket {self.barcode} for reservation {self.reservation.reservation_code}"
