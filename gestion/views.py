from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse # Importar reverse para obtener URLs de forma dinámica
from .forms import PassengerForm
from django.contrib.auth.decorators import login_required
from .services import FlightService, PassengerService, BookingService, NotificationService
from django.contrib import messages
from .models import Notification, Booking

# Vista para listar vuelos y permitir la búsqueda.
def flight_list(request):
    flight_service = FlightService()
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    departure_date = request.GET.get('departure_date')

    flights = flight_service.search_flights(origin, destination, departure_date)
    return render(request, 'gestion/flight_list.html', {'flights': flights})

# Vista para mostrar los detalles de un vuelo específico y sus asientos.
def flight_detail(request, flight_id):
    flight_service = FlightService()
    flight, seats = flight_service.get_flight_details(flight_id)
    return render(request, 'gestion/flight_detail.html', {'flight': flight, 'seats': seats})

# Vista para reservar un asiento en un vuelo. Requiere que el usuario esté autenticado.
@login_required
def book_seat(request, seat_id):
    booking_service = BookingService()
    if request.method == 'POST':
        try:
            booking = booking_service.book_seat(seat_id, request.user)
            messages.success(request, "Asiento reservado con éxito. Por favor, complete el pago.")
            return redirect('process_payment', booking_id=booking.id)
        except Exception as e:
            messages.error(request, str(e))
            # En caso de error, obtenemos el asiento nuevamente para redirigir al detalle del vuelo.
            # Asegúrate de que el modelo Seat esté importado si no lo está ya.
            from .models import Seat
            seat = get_object_or_404(Seat, id=seat_id)
            return redirect('flight_detail', flight_id=seat.flight.id)
    else:
        # Si la solicitud no es POST, simplemente renderiza la página de reserva de asiento.
        return render(request, 'gestion/book_seat.html', {'seat_id': seat_id})

# Vista para mostrar los detalles de un boleto/reserva. Requiere que el usuario esté autenticado.
@login_required
def ticket(request, booking_id):
    booking_service = BookingService()
    booking = booking_service.get_ticket(booking_id)
    return render(request, 'gestion/ticket.html', {'booking': booking})

# Vista para procesar el pago de una reserva. Requiere que el usuario esté autenticado.
@login_required
def process_payment(request, booking_id):
    booking_service = BookingService()
    # Obtiene la reserva, asegurándose de que pertenezca al usuario actual.
    booking = get_object_or_404(Booking, id=booking_id, passenger__user=request.user)

    if request.method == 'POST':
        try:
            # En un escenario real, aquí se integrarían con una pasarela de pago.
            # Por ahora, se simula el procesamiento del pago.
            booking = booking_service.process_payment(booking_id)
            messages.success(request, "¡Pago exitoso! Su reserva ha sido confirmada.")
            return redirect('ticket', booking_id=booking.id)
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado: {e}")
    else:
        messages.info(request, "Por favor, confirme su pago para esta reserva.")

    return render(request, 'gestion/payment_confirmation.html', {'booking': booking})

# Importa el decorador para restringir el acceso a miembros del staff.
from django.contrib.admin.views.decorators import staff_member_required

# Vista para generar un reporte de pasajeros por vuelo. Solo accesible para miembros del staff.
@staff_member_required
def passenger_report_by_flight(request, flight_id):
    flight_service = FlightService()
    flight, bookings = flight_service.get_passenger_report(flight_id)
    return render(request, 'gestion/passenger_report.html', {'flight': flight, 'bookings': bookings})

# Vista para crear un nuevo pasajero.
def create_passenger(request):
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            passenger_service = PassengerService()
            passenger_service.create_passenger(
                form.cleaned_data['first_name'],
                form.cleaned_data['last_name'],
                form.cleaned_data['document_id'],
                form.cleaned_data['email'],
                form.cleaned_data['phone']
            )
            messages.success(request, "¡Pasajero creado con éxito! Ahora puede iniciar sesión.")
            return redirect('login')
    else:
        form = PassengerForm()
    return render(request, 'gestion/create_passenger.html', {'form': form})

# Vista para mostrar el perfil del usuario autenticado y sus reservas.
# Vista para mostrar el perfil del usuario autenticado y sus reservas.
@login_required
def user_profile(request):
    # Si el usuario es un miembro del staff (administrador), redirigirlo al panel de administración.
    if request.user.is_staff:
        return redirect(reverse('admin:index')) # Redirige a la URL del panel de administración de Django.

    passenger_service = PassengerService()
    booking_service = BookingService()
    passenger = passenger_service.get_passenger_by_user(request.user)
    bookings = booking_service.get_bookings_by_passenger(passenger)
    return render(request, 'gestion/user_profile.html', {'passenger': passenger, 'bookings': bookings})

# Vista para editar el perfil del usuario autenticado.
@login_required
def edit_profile(request):
    passenger_service = PassengerService()
    passenger = passenger_service.get_passenger_by_user(request.user)
    if request.method == 'POST':
        form = PassengerForm(request.POST, instance=passenger)
        if form.is_valid():
            passenger_service.update_passenger(passenger, form.cleaned_data)
            messages.success(request, "Su perfil ha sido actualizado exitosamente.")
            return redirect('user_profile')
    else:
        form = PassengerForm(instance=passenger)
    return render(request, 'gestion/edit_profile.html', {'form': form})

# Vista para mostrar las notificaciones no leídas del usuario autenticado.
@login_required
def notifications(request):
    notification_service = NotificationService()
    unread_notifications = notification_service.get_unread_notifications(request.user)
    return render(request, 'gestion/notifications.html', {'notifications': unread_notifications})

# Vista para marcar una notificación específica como leída.
@login_required
def mark_notification_read(request, notification_id):
    notification_service = NotificationService()
    # Obtiene la notificación, asegurándose de que pertenezca al usuario actual.
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification_service.mark_notification_as_read(notification)
    messages.info(request, "Notificación marcada como leída.")
    return redirect('notifications')
