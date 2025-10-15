from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
from .validators import (
    validate_positive_number, validate_year_of_manufacture, validate_phone_number,
    validate_date_of_birth, validate_single_letter_column, validate_password_length
)

class SeatLayout(models.Model):
    layout_name = models.CharField(max_length=100, unique=True)
    rows = models.IntegerField()
    columns = models.IntegerField() # Max number of columns

    def __str__(self):
        return self.layout_name

    def clean(self):
        errors = {}
        try:
            validate_positive_number(self.rows, 'rows')
        except ValidationError as e:
            errors.update(e.message_dict)
        try:
            validate_positive_number(self.columns, 'columns')
        except ValidationError as e:
            errors.update(e.message_dict)
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
        try:
            validate_year_of_manufacture(self.year_of_manufacture)
        except ValidationError as e:
            errors.update(e.message_dict)
        try:
            validate_positive_number(self.capacity, 'capacity')
        except ValidationError as e:
            errors.update(e.message_dict)
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
        try:
            validate_positive_number(self.base_price, 'base_price')
        except ValidationError as e:
            errors.update(e.message_dict)
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
        try:
            validate_date_of_birth(self.date_of_birth)
        except ValidationError as e:
            errors.update(e.message_dict)
        try:
            validate_phone_number(self.phone)
        except ValidationError as e:
            errors.update(e.message_dict)
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
        try:
            validate_positive_number(self.price_paid, 'price_paid')
        except ValidationError as e:
            errors.update(e.message_dict)
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
        try:
            validate_positive_number(self.price_multiplier, 'price_multiplier')
        except ValidationError as e:
            errors.update(e.message_dict)
        if errors:
            raise ValidationError(errors)

class SeatLayoutPosition(models.Model):
    seat_layout = models.ForeignKey(SeatLayout, on_delete=models.CASCADE, related_name='positions')
    seat_type = models.ForeignKey(SeatType, on_delete=models.CASCADE)
    row = models.IntegerField()
    column = models.CharField(max_length=2)

    class Meta:
        unique_together = (('seat_layout', 'row', 'column'),)

    @property
    def seat_number(self):
        return f"{self.row}{self.column}"

    def __str__(self):
        return f"{self.seat_layout.layout_name} - Row {self.row}, Col {self.column} ({self.seat_type.code})"

    def clean(self):
        errors = {}
        try:
            validate_positive_number(self.row, 'row')
        except ValidationError as e:
            errors.update(e.message_dict)
        try:
            validate_single_letter_column(self.column)
        except ValidationError as e:
            errors.update(e.message_dict)
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
        try:
            validate_positive_number(self.row, 'row')
        except ValidationError as e:
            errors.update(e.message_dict)
        try:
            validate_single_letter_column(self.column)
        except ValidationError as e:
            errors.update(e.message_dict)
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
        
        errors = {}
        try:
            validate_positive_number(self.price, 'price')
        except ValidationError as e:
            errors.update(e.message_dict)
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
        else:
            try:
                validate_password_length(self.password)
            except ValidationError as e:
                errors.update(e.message_dict)
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

    @property
    def ticket_number(self):
        return self.barcode

    def __str__(self):
        return f"Ticket {self.ticket_number} for reservation {self.reservation.reservation_code}"
