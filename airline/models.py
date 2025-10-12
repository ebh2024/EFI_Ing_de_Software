from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

class SeatLayout(models.Model):
    layout_name = models.CharField(max_length=100, unique=True)
    rows = models.IntegerField()
    columns = models.IntegerField() # Max number of columns

    def __str__(self):
        return self.layout_name

    def clean(self):
        errors = {}
        if self.rows is not None and self.rows <= 0:
            errors['rows'] = 'Rows must be a positive number.'
        if self.columns is not None and self.columns <= 0:
            errors['columns'] = 'Columns must be a positive number.'
        if errors:
            raise ValidationError(errors)

class Airplane(models.Model):
    model_name = models.CharField(max_length=100, default="Default Model")
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=20, unique=True, default=uuid.uuid4().hex[:20])
    year_of_manufacture = models.IntegerField(blank=True, null=True)
    capacity = models.IntegerField()
    seat_layout = models.ForeignKey(SeatLayout, on_delete=models.SET_NULL, null=True, blank=True)
    last_maintenance_date = models.DateField(blank=True, null=True)
    technical_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.model_name} ({self.registration_number})"

    def clean(self):
        errors = {}
        current_year = timezone.now().year
        if self.year_of_manufacture and (self.year_of_manufacture < 1900 or self.year_of_manufacture > current_year + 5): # Allowing a small future window for planning
            errors['year_of_manufacture'] = f'Year of manufacture must be between 1900 and {current_year + 5}.'
        if self.capacity is not None and self.capacity <= 0:
            errors['capacity'] = 'Capacity must be a positive number.'
        if errors:
            raise ValidationError(errors)

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
        errors = {}
        if self.arrival_date and self.departure_date and self.arrival_date <= self.departure_date:
            errors['arrival_date'] = 'Arrival date must be after departure date.'
        if self.departure_date and self.departure_date < timezone.now():
            errors['departure_date'] = 'Departure date cannot be in the past.'

        if self.base_price is not None and self.base_price <= 0:
            errors['base_price'] = 'Base price must be a positive number.'

        if errors:
            raise ValidationError(errors)

class Passenger(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('DNI', 'National Identity Document'),
        ('PAS', 'Passport'),
        ('LE', 'Enrollment Booklet'),
        ('LC', 'Civic Booklet'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    document_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField()
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPE_CHOICES, default='DNI')

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    def clean(self):
        errors = {}
        if not self.first_name:
            errors['first_name'] = 'First name cannot be empty.'
        if not self.document_number:
            errors['document_number'] = 'Document number cannot be empty.'
        # Django's EmailField handles basic email format validation.
        # The unique=True constraint handles duplicate emails.
        # We can rely on Django's built-in validation for these.
        pass
        if self.date_of_birth and self.date_of_birth >= timezone.now().date():
            errors['date_of_birth'] = 'Date of birth cannot be in the future.'
        # Basic phone number validation (digits only, min 7, max 15)
        if self.phone and not self.phone.isdigit():
            errors['phone'] = 'Phone number must contain only digits.'
        if self.phone and (len(self.phone) < 7 or len(self.phone) > 15):
            errors['phone'] = 'Phone number must be between 7 and 15 digits long.'

        if errors:
            raise ValidationError(errors)

class FlightHistory(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='flight_history')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    seat_number = models.CharField(max_length=10, blank=True, null=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.passenger.first_name}'s flight on {self.flight.departure_date}"

    def clean(self):
        errors = {}
        if self.price_paid is not None and self.price_paid <= 0:
            errors['price_paid'] = 'Price paid must be a positive number.'
        if errors:
            raise ValidationError(errors)

class SeatType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}
        if self.price_multiplier is not None and self.price_multiplier <= 0:
            errors['price_multiplier'] = 'Price multiplier must be a positive number.'
        if errors:
            raise ValidationError(errors)

class SeatLayoutPosition(models.Model):
    seat_layout = models.ForeignKey(SeatLayout, on_delete=models.CASCADE, related_name='positions')
    seat_type = models.ForeignKey(SeatType, on_delete=models.CASCADE)
    row = models.IntegerField()
    column = models.CharField(max_length=2)

    class Meta:
        unique_together = (('seat_layout', 'row', 'column'),)

    def __str__(self):
        return f"{self.seat_layout.layout_name} - Row {self.row}, Col {self.column} ({self.seat_type.code})"

    def clean(self):
        errors = {}
        if self.row is not None and self.row <= 0:
            errors['row'] = 'Row must be a positive number.'
        if not self.column.isalpha() or len(self.column) > 1: # Assuming column is a single letter
            errors['column'] = 'Column must be a single letter (e.g., A, B).'
        if errors:
            raise ValidationError(errors)

class Seat(models.Model):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    row = models.IntegerField()
    column = models.CharField(max_length=2)
    seat_type = models.ForeignKey(SeatType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20) # E.g.: 'Available', 'Occupied', 'Reserved'

    def __str__(self):
        return f"Seat {self.number} - {self.airplane.model_name}"

    def clean(self):
        errors = {}
        if self.row is not None and self.row <= 0:
            errors['row'] = 'Row must be a positive number.'
        if not self.column.isalpha() or len(self.column) > 1: # Assuming column is a single letter
            errors['column'] = 'Column must be a single letter (e.g., A, B).'
        if errors:
            raise ValidationError(errors)

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
        
        errors = {} # Initialize errors dictionary
        if self.price is not None and self.price <= 0:
            errors['price'] = 'Price must be a positive number.'

        if errors:
            raise ValidationError(errors)

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

    def clean(self):
        errors = {}
        if not self.username:
            errors['username'] = 'Username cannot be empty.'
        if not self.password:
            errors['password'] = 'Password cannot be empty.'
        elif len(self.password) < 8:
            errors['password'] = 'Password must be at least 8 characters long.'
        if not self.email:
            errors['email'] = 'Email cannot be empty.'
        elif '@' not in self.email:
            errors['email'] = 'Invalid email format.'
        
        if errors:
            raise ValidationError(errors)

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
