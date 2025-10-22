from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from .validators import (
    validate_positive_number, validate_year_of_manufacture, validate_phone_number,
    validate_date_of_birth, validate_single_letter_column, validate_password_length
)

class SeatLayout(models.Model):
    """
    Modelo que representa el diseño de asientos de un avión.

    Este modelo define la estructura básica de filas y columnas para los asientos
    en un avión, permitiendo configurar diferentes layouts de asientos.

    Atributos:
        layout_name (str): Nombre único del layout de asientos.
        rows (int): Número de filas en el layout.
        columns (int): Número máximo de columnas en el layout.
    """
    layout_name = models.CharField(_('layout name'), max_length=100, unique=True)
    rows = models.IntegerField(_('rows'))
    columns = models.IntegerField(_('columns')) # Max number of columns

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
    """
    Modelo que representa un avión en el sistema de gestión de aerolíneas.

    Este modelo almacena información detallada sobre cada avión, incluyendo
    su modelo, fabricante, capacidad y layout de asientos.

    Atributos:
        model_name (str): Nombre del modelo del avión.
        manufacturer (str): Fabricante del avión (opcional).
        registration_number (str): Número de registro único del avión.
        year_of_manufacture (int): Año de fabricación (opcional).
        capacity (int): Capacidad total de pasajeros.
        seat_layout (SeatLayout): Layout de asientos asociado (opcional).
        last_maintenance_date (date): Fecha del último mantenimiento (opcional).
        technical_notes (str): Notas técnicas adicionales (opcional).
    """
    model_name = models.CharField(_('model name'), max_length=100, default="Default Model")
    manufacturer = models.CharField(_('manufacturer'), max_length=100, blank=True, null=True)
    registration_number = models.CharField(_('registration number'), max_length=20, unique=True, default=uuid.uuid4().hex[:20])
    year_of_manufacture = models.IntegerField(_('year of manufacture'), blank=True, null=True)
    capacity = models.IntegerField(_('capacity'))
    seat_layout = models.ForeignKey(SeatLayout, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('seat layout'))
    last_maintenance_date = models.DateField(_('last maintenance date'), blank=True, null=True)
    technical_notes = models.TextField(_('technical notes'), blank=True, null=True)

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
    """
    Modelo que representa un vuelo en el sistema de aerolíneas.

    Este modelo contiene toda la información necesaria sobre un vuelo específico,
    incluyendo avión, rutas, horarios y precios base.

    Atributos:
        airplane (Airplane): Avión asignado al vuelo.
        origin (str): Ciudad o aeropuerto de origen.
        destination (str): Ciudad o aeropuerto de destino.
        departure_date (datetime): Fecha y hora de salida.
        arrival_date (datetime): Fecha y hora de llegada.
        duration (timedelta): Duración estimada del vuelo.
        status (str): Estado actual del vuelo.
        base_price (Decimal): Precio base del vuelo.
    """
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, verbose_name=_('airplane'))
    origin = models.CharField(_('origin'), max_length=100)
    destination = models.CharField(_('destination'), max_length=100)
    departure_date = models.DateTimeField(_('departure date'))
    arrival_date = models.DateTimeField(_('arrival date'))
    duration = models.DurationField(_('duration'))
    status = models.CharField(_('status'), max_length=50)
    base_price = models.DecimalField(_('base price'), max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Flight {self.origin} to {self.destination} on {self.departure_date.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        errors = {}
        if self.arrival_date and self.departure_date and self.arrival_date <= self.departure_date:
            errors['arrival_date'] = _('Arrival date must be after departure date.')
        if self.departure_date and self.departure_date < timezone.now():
            errors['departure_date'] = _('Departure date cannot be in the past.')
        try:
            validate_positive_number(self.base_price, 'base_price')
        except ValidationError as e:
            errors.update(e.message_dict)
        if errors:
            raise ValidationError(errors)

class Passenger(models.Model):
    """
    Modelo que representa a un pasajero en el sistema de aerolíneas.

    Este modelo almacena la información personal y de identificación de los pasajeros
    que utilizan el sistema para reservar vuelos.

    Atributos:
        DOCUMENT_TYPE_CHOICES (list): Opciones para tipos de documento.
        first_name (str): Nombre del pasajero.
        last_name (str): Apellido del pasajero (opcional).
        document_number (str): Número de documento único.
        email (str): Correo electrónico único.
        phone (str): Número de teléfono (opcional).
        date_of_birth (date): Fecha de nacimiento.
        document_type (str): Tipo de documento de identificación.
    """
    DOCUMENT_TYPE_CHOICES = [
        ('DNI', _('National Identity Document')),
        ('PAS', _('Passport')),
        ('LE', _('Enrollment Booklet')),
        ('LC', _('Civic Booklet')),
    ]
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100, blank=True, null=True)
    document_number = models.CharField(_('document number'), max_length=20, unique=True)
    email = models.EmailField(_('email'), unique=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'))
    document_type = models.CharField(_('document type'), max_length=3, choices=DOCUMENT_TYPE_CHOICES, default='DNI')

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    def clean(self):
        errors = {}
        if not self.first_name:
            errors['first_name'] = _('First name cannot be empty.')
        if not self.document_number:
            errors['document_number'] = _('Document number cannot be empty.')
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
    """
    Modelo que registra el historial de vuelos de un pasajero.

    Este modelo mantiene un registro de los vuelos que un pasajero ha tomado,
    incluyendo detalles de reserva y precio pagado.

    Atributos:
        passenger (Passenger): Pasajero asociado al historial.
        flight (Flight): Vuelo correspondiente.
        booking_date (datetime): Fecha de reserva (automática).
        seat_number (str): Número de asiento (opcional).
        price_paid (Decimal): Precio pagado (opcional).
    """
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
    """
    Modelo que define los tipos de asientos disponibles.

    Este modelo clasifica los asientos por categorías como económica, business, etc.,
    con un multiplicador de precio para calcular el costo adicional.

    Atributos:
        name (str): Nombre del tipo de asiento (único).
        code (str): Código abreviado del tipo de asiento (único).
        price_multiplier (Decimal): Multiplicador para el precio base.
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    code = models.CharField(_('code'), max_length=10, unique=True)
    price_multiplier = models.DecimalField(_('price multiplier'), max_digits=5, decimal_places=2, default=1.00)

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
    """
    Modelo que define la posición de un asiento en un layout específico.

    Este modelo asocia una fila y columna específicas con un tipo de asiento
    dentro de un layout de avión, asegurando unicidad por layout.

    Atributos:
        seat_layout (SeatLayout): Layout de asientos al que pertenece.
        seat_type (SeatType): Tipo de asiento en esta posición.
        row (int): Número de fila.
        column (str): Letra de columna.

    Propiedades:
        seat_number (str): Número completo del asiento (fila + columna).
    """
    seat_layout = models.ForeignKey(SeatLayout, on_delete=models.CASCADE, related_name='positions', verbose_name=_('seat layout'))
    seat_type = models.ForeignKey(SeatType, on_delete=models.CASCADE, verbose_name=_('seat type'))
    row = models.IntegerField(_('row'))
    column = models.CharField(_('column'), max_length=2)

    class Meta:
        unique_together = (('seat_layout', 'row', 'column'),)

    @property
    def seat_number(self):
        """
        Propiedad que devuelve el número completo del asiento.

        Returns:
            str: Número del asiento en formato "fila + columna".
        """
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
    """
    Modelo que representa un asiento específico en un avión.

    Este modelo define cada asiento individual con su número, posición
    y estado actual para el sistema de reservas.

    Atributos:
        airplane (Airplane): Avión al que pertenece el asiento.
        number (str): Número del asiento.
        row (int): Fila del asiento.
        column (str): Columna del asiento.
        seat_type (SeatType): Tipo de asiento (opcional).
        status (str): Estado del asiento (Available, Occupied, Reserved).
    """
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
    """
    Modelo que representa una reserva de asiento en un vuelo.

    Este modelo gestiona las reservas de asientos, incluyendo el estado,
    precio y restricciones de unicidad por vuelo y pasajero.

    Atributos:
        RESERVATION_STATUS_CHOICES (list): Opciones de estado de reserva.
        flight (Flight): Vuelo reservado.
        passenger (Passenger): Pasajero que realiza la reserva.
        seat (Seat): Asiento reservado.
        status (str): Estado de la reserva.
        reservation_date (datetime): Fecha de la reserva (automática).
        price (Decimal): Precio de la reserva.
        reservation_code (str): Código único de la reserva.
    """
    RESERVATION_STATUS_CHOICES = [
        ('PEN', _('Pending')),
        ('CON', _('Confirmed')),
        ('CAN', _('Cancelled')),
        ('PAID', _('Paid')),
    ]
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, verbose_name=_('flight'))
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, verbose_name=_('passenger'))
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, verbose_name=_('seat'))
    status = models.CharField(_('status'), max_length=4, choices=RESERVATION_STATUS_CHOICES, default='PEN')
    reservation_date = models.DateTimeField(_('reservation date'), auto_now_add=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    reservation_code = models.CharField(_('reservation code'), max_length=20, unique=True)

    class Meta:
        unique_together = (('flight', 'seat'), ('flight', 'passenger'))

    def __str__(self):
        return f"Reservation {self.reservation_code} for {self.passenger.first_name} on flight {self.flight.id}"

    def clean(self):
        """
        Valida los datos del modelo antes de guardar.

        Verifica restricciones de unicidad y consistencia de estados de asientos.

        Raises:
            ValidationError: Si hay errores de validación.
        """
        # Restriction: A seat cannot be reserved more than once per flight (already covered by unique_together)
        # Restriction: A passenger cannot have more than one reservation per flight (already covered by unique_together)

        self._validate_seat_status_consistency()

        errors = {}
        try:
            validate_positive_number(self.price, 'price')
        except ValidationError as e:
            errors.update(e.message_dict)
        if errors:
            raise ValidationError(errors)

    def _validate_seat_status_consistency(self):
        """
        Valida la consistencia entre el estado de la reserva y el estado del asiento.

        Raises:
            ValidationError: Si el estado del asiento no es consistente con la reserva.
        """
        # Restriction: Seat statuses must be consistent with reservations
        if self.status == 'CON' or self.status == 'PAID':
            if self.seat.status not in ['Reserved', 'Occupied']:
                raise ValidationError(_('The seat must be in "Reserved" or "Occupied" status for a confirmed/paid reservation.'))
        elif self.status == 'CAN':
            if self.seat.status != 'Available':
                raise ValidationError(_('The seat must be in "Available" status for a cancelled reservation.'))

    def save(self, *args, **kwargs):
        """
        Guarda la instancia del modelo, actualizando el estado del asiento asociado.

        Args:
            *args: Argumentos posicionales para el método save.
            **kwargs: Argumentos de palabra clave para el método save.

        Efectos secundarios:
            Actualiza el estado del asiento según el estado de la reserva.
        """
        self._update_associated_seat_status()
        super().save(*args, **kwargs)

    def _update_associated_seat_status(self):
        """
        Actualiza el estado del asiento asociado basado en el estado de la reserva.

        Efectos secundarios:
            Modifica y guarda el estado del asiento relacionado.
        """
        # Update seat status when saving the reservation
        if self.status in ['CON', 'PAID']:
            self.seat.status = 'Reserved'
        elif self.status == 'CAN':
            self.seat.status = 'Available'
        self.seat.save()

class UserProfile(models.Model):
    """
    Modelo que representa el perfil de usuario en el sistema.

    Este modelo maneja la autenticación y roles de usuarios,
    incluyendo administradores, empleados y clientes.

    Atributos:
        ROLE_CHOICES (list): Opciones de roles disponibles.
        username (str): Nombre de usuario único.
        password (str): Contraseña del usuario.
        email (str): Correo electrónico único.
        role (str): Rol del usuario en el sistema.
    """
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
    """
    Modelo que representa un ticket de vuelo emitido.

    Este modelo gestiona los tickets físicos o electrónicos generados
    a partir de reservas confirmadas.

    Atributos:
        TICKET_STATUS_CHOICES (list): Opciones de estado del ticket.
        reservation (Reservation): Reserva asociada al ticket.
        barcode (str): Código de barras único del ticket.
        issue_date (datetime): Fecha de emisión (automática).
        status (str): Estado actual del ticket.

    Propiedades:
        ticket_number (str): Número del ticket (igual al barcode).
    """
    TICKET_STATUS_CHOICES = [
        ('EMI', _('Issued')),
        ('CAN', _('Cancelled')),
        ('USED', _('Used')),
    ]
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, verbose_name=_('reservation'))
    barcode = models.CharField(_('barcode'), max_length=50, unique=True)
    issue_date = models.DateTimeField(_('issue date'), auto_now_add=True)
    status = models.CharField(_('status'), max_length=4, choices=TICKET_STATUS_CHOICES, default='EMI')

    @property
    def ticket_number(self):
        """
        Propiedad que devuelve el número del ticket.

        Returns:
            str: Número del ticket (código de barras).
        """
        return self.barcode

    def __str__(self):
        return f"Ticket {self.ticket_number} for reservation {self.reservation.reservation_code}"
