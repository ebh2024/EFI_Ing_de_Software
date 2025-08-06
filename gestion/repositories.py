from .models import Flight, Passenger, Aircraft, Booking, Seat, Notification

# Repositorio para interactuar con el modelo Flight.
class FlightRepository:
    # Obtiene todos los objetos Flight.
    def get_all(self):
        return Flight.objects.all()

    # Obtiene un objeto Flight por su ID.
    def get_by_id(self, flight_id):
        return Flight.objects.get(pk=flight_id)

# Repositorio para interactuar con el modelo Passenger.
class PassengerRepository:
    # Obtiene un objeto Passenger asociado a un usuario dado.
    def get_by_user(self, user):
        return Passenger.objects.get(user=user)

    # Obtiene un objeto Passenger o lo crea si no existe, asociado a un usuario dado.
    def get_or_create_by_user(self, user):
        return Passenger.objects.get_or_create(user=user, defaults={'first_name': '', 'last_name': '', 'document_id': '', 'email': user.email, 'phone': ''})

    # Crea un nuevo objeto Passenger.
    def create(self, user, first_name, last_name, document_id, email, phone):
        return Passenger.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            document_id=document_id,
            email=email,
            phone=phone
        )
    
    # Guarda un objeto Passenger existente.
    def save(self, passenger):
        passenger.save()

# Repositorio para interactuar con el modelo Seat.
class SeatRepository:
    # Obtiene un objeto Seat por su ID.
    def get_by_id(self, seat_id):
        return Seat.objects.get(pk=seat_id)

    # Obtiene todos los objetos Seat asociados a un vuelo dado.
    def get_by_flight(self, flight):
        return Seat.objects.filter(flight=flight)

    # Guarda un objeto Seat existente.
    def save(self, seat):
        seat.save()

# Repositorio para interactuar con el modelo Booking.
class BookingRepository:
    # Crea un nuevo objeto Booking.
    def create(self, flight, passenger, seat):
        return Booking.objects.create(
            flight=flight,
            passenger=passenger,
            seat=seat
        )

    # Obtiene un objeto Booking por su ID.
    def get_by_id(self, booking_id):
        return Booking.objects.get(pk=booking_id)

    # Obtiene todos los objetos Booking asociados a un vuelo dado.
    def get_by_flight(self, flight):
        return Booking.objects.filter(flight=flight)

    # Obtiene todos los objetos Booking asociados a un pasajero dado.
    def get_by_passenger(self, passenger):
        return Booking.objects.filter(passenger=passenger)

# Repositorio para interactuar con el modelo Notification.
class NotificationRepository:
    # Crea un nuevo objeto Notification.
    def create(self, recipient, message, flight=None):
        return Notification.objects.create(recipient=recipient, message=message, flight=flight)

    # Obtiene todas las notificaciones no leídas para un usuario dado.
    def get_unread_notifications(self, user):
        return Notification.objects.filter(recipient=user, is_read=False).order_by('-created_at')

    # Marca una notificación como leída.
    def mark_as_read(self, notification):
        notification.is_read = True
        notification.save()
