from .models import Flight, Seat, Passenger, Booking, Notification
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid # Importa uuid para generar IDs de transacción únicos.
import datetime # Import datetime for date parsing.

# Servicio para gestionar operaciones relacionadas con vuelos.
class FlightService:
    # Busca vuelos basándose en el origen, destino y fecha de salida.
    def search_flights(self, origin, destination, departure_date):
        flights = Flight.objects.all()
        if origin:
            flights = flights.filter(origin__icontains=origin)
        if destination:
            flights = flights.filter(destination__icontains=destination)
        if departure_date:
            try:
                # Parse the datetime string and extract only the date part
                parsed_date = datetime.datetime.strptime(departure_date, "%Y-%m-%d %H:%M").date()
                flights = flights.filter(departure_date__date=parsed_date)
            except ValueError:
                # If the format is already YYYY-MM-DD, or another valid date format,
                # Django's filter will handle it. If it's completely invalid,
                # the original error might still occur, but this handles the common case.
                flights = flights.filter(departure_date__date=departure_date)
        return flights

    # Obtiene los detalles de un vuelo específico y sus asientos asociados.
    def get_flight_details(self, flight_id):
        flight = get_object_or_404(Flight, id=flight_id)
        seats = Seat.objects.filter(flight=flight).order_by('number')
        return flight, seats

    # Obtiene un reporte de pasajeros para un vuelo específico (reservas completadas).
    def get_passenger_report(self, flight_id):
        flight = get_object_or_404(Flight, id=flight_id)
        bookings = Booking.objects.filter(flight=flight, payment_status='completed').select_related('passenger', 'seat')
        return flight, bookings

# Servicio para gestionar operaciones relacionadas con pasajeros.
class PassengerService:
    # Crea un nuevo pasajero y, si es necesario, un usuario asociado.
    def create_passenger(self, first_name, last_name, document_id, email, phone):
        # Intenta obtener un usuario existente o crea uno nuevo con el email como username.
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        if created:
            # Si el usuario es nuevo, establece una contraseña inutilizable para que la configure después.
            user.set_unusable_password()
            user.save()

        # Crea el objeto Passenger.
        passenger = Passenger.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            document_id=document_id,
            email=email,
            phone=phone
        )
        return passenger

    # Obtiene un pasajero por el objeto User asociado.
    def get_passenger_by_user(self, user):
        return get_object_or_404(Passenger, user=user)

    # Actualiza la información de un pasajero existente.
    def update_passenger(self, passenger, data):
        passenger.first_name = data.get('first_name', passenger.first_name)
        passenger.last_name = data.get('last_name', passenger.last_name)
        passenger.document_id = data.get('document_id', passenger.document_id)
        passenger.email = data.get('email', passenger.email)
        passenger.phone = data.get('phone', passenger.phone)
        passenger.save()
        return passenger

# Servicio para gestionar operaciones relacionadas con reservas.
class BookingService:
    # Realiza la reserva de un asiento para un usuario.
    def book_seat(self, seat_id, user):
        with transaction.atomic(): # Asegura que todas las operaciones se completen o se reviertan.
            seat = get_object_or_404(Seat, id=seat_id)
            if seat.status != 'available':
                raise ValidationError("Seat is not available.")

            passenger = get_object_or_404(Passenger, user=user)

            # Verifica si el pasajero ya tiene una reserva completada para este vuelo.
            if Booking.objects.filter(flight=seat.flight, passenger=passenger, payment_status='completed').exists():
                raise ValidationError("You already have a completed booking for this flight.")

            # Crea una reserva con estado pendiente de pago.
            booking = Booking.objects.create(
                flight=seat.flight,
                passenger=passenger,
                seat=seat,
                payment_status='pending'
            )
            seat.status = 'reserved' # Marca el asiento como reservado.
            seat.save()
            return booking

    # Obtiene los detalles de una reserva por su ID.
    def get_ticket(self, booking_id):
        return get_object_or_404(Booking, id=booking_id)

    # Obtiene todas las reservas de un pasajero, ordenadas por fecha de reserva.
    def get_bookings_by_passenger(self, passenger):
        return Booking.objects.filter(passenger=passenger).order_by('-booking_date')

    # Procesa el pago de una reserva.
    def process_payment(self, booking_id):
        with transaction.atomic(): # Asegura la atomicidad de la transacción de pago.
            booking = get_object_or_404(Booking, id=booking_id)

            if booking.payment_status == 'completed':
                raise ValidationError("Payment for this booking has already been completed.")

            # Simulación del procesamiento de pago. En una aplicación real, se integraría con una pasarela de pago.
            payment_successful = True # Simula un pago exitoso.

            if payment_successful:
                booking.payment_status = 'completed'
                booking.transaction_id = str(uuid.uuid4()) # Genera un ID de transacción único.
                booking.payment_date = timezone.now() # Registra la fecha y hora del pago.
                booking.save()

                # Actualiza el estado del asiento a 'occupied' si el pago es exitoso.
                if booking.seat:
                    booking.seat.status = 'occupied'
                    booking.seat.save()

                # Envía una notificación al usuario sobre el pago exitoso.
                NotificationService().create_notification(
                    booking.passenger.user,
                    f"Your payment for flight {booking.flight.origin} to {booking.flight.destination} has been successfully processed. Booking ID: {booking.id}",
                    booking.flight
                )
                return booking
            else:
                booking.payment_status = 'failed'
                booking.save()
                raise ValidationError("Payment failed. Please try again.")

    # Cancela una reserva.
    def cancel_booking(self, booking):
        with transaction.atomic():
            if booking.payment_status == 'cancelled':
                raise ValidationError("This booking has already been cancelled.")

            booking.payment_status = 'cancelled'
            booking.save()

            if booking.seat:
                booking.seat.status = 'available'
                booking.seat.save()

            # Envía una notificación al usuario sobre la cancelación.
            NotificationService().create_notification(
                booking.passenger.user,
                f"Your booking for flight {booking.flight.origin} to {booking.flight.destination} has been cancelled. Booking ID: {booking.id}",
                booking.flight
            )

# Servicio para gestionar operaciones relacionadas con notificaciones.
class NotificationService:
    # Crea una nueva notificación para un destinatario.
    def create_notification(self, recipient, message, flight=None):
        Notification.objects.create(recipient=recipient, message=message, flight=flight)

    # Obtiene todas las notificaciones no leídas para un usuario, ordenadas por fecha de creación.
    def get_unread_notifications(self, user):
        return Notification.objects.filter(recipient=user, is_read=False).order_by('-created_at')

    # Marca una notificación como leída.
    def mark_notification_as_read(self, notification):
        notification.is_read = True
        notification.save()
