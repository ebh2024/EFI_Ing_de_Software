from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Modelo para representar un tipo de aeronave.
class Aircraft(models.Model):
    # El modelo o nombre de la aeronave (ej. "Boeing 737").
    model = models.CharField(max_length=100)
    # La capacidad total de pasajeros de la aeronave.
    capacity = models.IntegerField()
    # Un campo JSON para almacenar el diseño de los asientos (ej. filas y números de asiento).
    seat_layout = models.JSONField(default=dict)
    # Información técnica adicional sobre la aeronave.
    technical_information = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.model

# Modelo para representar un vuelo.
class Flight(models.Model):
    # Origen del vuelo.
    origin = models.CharField(max_length=100)
    # Destino del vuelo.
    destination = models.CharField(max_length=100)
    # Fecha y hora de salida del vuelo.
    departure_date = models.DateTimeField()
    # Fecha y hora de llegada del vuelo.
    arrival_date = models.DateTimeField()
    # Precio del vuelo.
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Aeronave asignada a este vuelo. Relación ForeignKey con Aircraft.
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.origin} to {self.destination}"

    # Valida que la fecha de llegada sea posterior a la fecha de salida.
    def clean(self):
        if self.arrival_date <= self.departure_date:
            raise ValidationError(_('Arrival date must be after departure date.'))

    # Sobrescribe el método save para ejecutar la validación y crear asientos si es necesario.
    def save(self, *args, **kwargs):
        self.clean() # Ejecuta la validación antes de guardar.
        super().save(*args, **kwargs)
        # Si se asigna una aeronave y no existen asientos para este vuelo, los crea.
        if self.aircraft and not Seat.objects.filter(flight=self).exists():
            layout = self.aircraft.seat_layout
            for row in layout.get('rows', []):
                for seat_info in row.get('seats', []):
                    Seat.objects.create(flight=self, number=seat_info['number'])

# Modelo para representar un pasajero.
class Passenger(models.Model):
    # Vincula el pasajero a un usuario del sistema de autenticación de Django.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Nombre del pasajero.
    first_name = models.CharField(max_length=100)
    # Apellido del pasajero.
    last_name = models.CharField(max_length=100)
    # Número de documento de identidad del pasajero (ej. DNI, Pasaporte). Debe ser único.
    document_id = models.CharField(max_length=20, null=True, unique=True)
    # Dirección de correo electrónico del pasajero.
    email = models.EmailField()
    # Número de teléfono del pasajero.
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Retorna el historial de reservas del pasajero.
    def flight_history(self):
        return self.booking_set.all()

# Modelo para representar un asiento específico en un vuelo.
class Seat(models.Model):
    # Opciones para el estado del asiento.
    STATUS_CHOICES = (
        ('available', _('Available')), # Asiento disponible para reserva.
        ('reserved', _('Reserved')), # Asiento reservado (pendiente de pago).
        ('occupied', _('Occupied')), # Asiento ocupado (pago completado).
    )
    # Vuelo al que pertenece este asiento. Relación ForeignKey con Flight.
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    # Número o identificador del asiento (ej. "1A", "23B").
    number = models.CharField(max_length=10)
    # Estado actual del asiento.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return _("Seat %(number)s on flight %(flight)s") % {'number': self.number, 'flight': self.flight}

# Modelo para representar una reserva de vuelo.
class Booking(models.Model):
    # Opciones para el estado del pago de la reserva.
    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')), # Pago pendiente.
        ('completed', _('Completed')), # Pago completado.
        ('failed', _('Failed')), # Pago fallido.
        ('refunded', _('Refunded')), # Pago reembolsado.
    )
    # Vuelo asociado a esta reserva. Relación ForeignKey con Flight.
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    # Pasajero que realiza la reserva. Relación ForeignKey con Passenger.
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    # Asiento reservado. Relación OneToOneField con Seat (un asiento solo puede tener una reserva activa).
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, null=True)
    # Fecha y hora en que se realizó la reserva. Se establece automáticamente al crear.
    booking_date = models.DateTimeField(auto_now_add=True)
    # Estado actual del pago de la reserva.
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    # ID de la transacción de pago, si aplica.
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    # Fecha y hora en que se completó el pago.
    payment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return _("Booking for %(passenger)s on flight %(flight)s, seat %(seat)s") % {'passenger': self.passenger, 'flight': self.flight, 'seat': self.seat.number}

# Modelo para representar una notificación para un usuario.
class Notification(models.Model):
    # Usuario que recibe la notificación. Relación ForeignKey con User.
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    # Contenido del mensaje de la notificación.
    message = models.TextField()
    # Fecha y hora en que se creó la notificación. Se establece automáticamente al crear.
    created_at = models.DateTimeField(auto_now_add=True)
    # Indica si la notificación ha sido leída por el usuario.
    is_read = models.BooleanField(default=False)
    # Vuelo opcional al que se vincula la notificación (ej. notificación de cambio de vuelo).
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:50]}..."
