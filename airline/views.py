from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ReservationForm, TicketForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ReservationForm, TicketForm
from .models import Flight, Passenger, FlightHistory, Seat, Reservation, Ticket
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

# Import CRUD views
from .crud_views import (
    flight_list, flight_create, flight_update, flight_delete,
    passenger_list, passenger_create, passenger_update, passenger_delete,
    airplane_list, airplane_create, airplane_update, airplane_delete,
    seat_layout_list, seat_layout_create, seat_layout_update, seat_layout_delete,
    seat_type_list, seat_type_create, seat_type_update, seat_type_delete,
    seat_layout_position_list, seat_layout_position_create, seat_layout_position_update, seat_layout_position_delete
)

# Import services
from .services import PassengerService, ReservationService, TicketService, FlightService

# Initialize services
passenger_service = PassengerService()
reservation_service = ReservationService()
ticket_service = TicketService()
flight_service = FlightService()

def home(request):
    flights = Flight.objects.all()
    return render(request, 'airline/home.html', {'flights': flights})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'airline/register.html', {'form': form})

@login_required
def passenger_flight_history(request, pk):
    passenger, flight_history = passenger_service.get_passenger_flight_history(pk)
    return render(request, 'airline/passenger_flight_history.html', {'passenger': passenger, 'flight_history': flight_history})

@login_required
def flight_detail_with_seats(request, pk):
    flight, seats_by_row = reservation_service.get_flight_details_with_seats(pk)
    return render(request, 'airline/flight_detail_with_seats.html', {
        'flight': flight,
        'seats_by_row': seats_by_row,
    })

@login_required
def reserve_seat(request, flight_pk, seat_pk):
    flight = get_object_or_404(Flight, pk=flight_pk)
    seat = get_object_or_404(Seat, pk=seat_pk)

    if _check_seat_availability(flight, seat):
        return render(request, 'airline/reservation_error.html', {'message': 'This seat is already reserved for this flight.'})

    passenger = passenger_service.get_or_create_passenger_for_user(request.user)

    if request.method == 'POST':
        return _handle_post_request(request, flight, seat, passenger)
    else:
        return _handle_get_request(request, flight, seat, passenger)

def _check_seat_availability(flight, seat):
    return reservation_service.reservation_repo.filter_by_flight_seat_status(flight, seat, ['PEN', 'CON', 'PAID']).exists()

def _handle_post_request(request, flight, seat, passenger):
    form = ReservationForm(request.POST, initial={'flight': flight})
    if form.is_valid():
        reservation = reservation_service.create_reservation(flight.pk, passenger.pk, seat.pk, form.cleaned_data['price'])
        return redirect('reservation_detail', pk=reservation.pk)
    else:
        print(form.errors)
        return render(request, 'airline/reserve_seat.html', {
            'form': form,
            'flight': flight,
            'seat': seat,
            'passenger': passenger,
            'action': 'Reserve'
        })

def _handle_get_request(request, flight, seat, passenger):
    form = ReservationForm(initial={'flight': flight, 'seat': seat, 'passenger': passenger, 'status': 'PEN'})
    return render(request, 'airline/reserve_seat.html', {
        'form': form,
        'flight': flight,
        'seat': seat,
        'passenger': passenger,
        'action': 'Reserve'
    })

@login_required
def reservation_list(request):
    reservations = reservation_service.get_reservations_list()
    return render(request, 'airline/reservation_list.html', {'reservations': reservations})

@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    return render(request, 'airline/reservation_detail.html', {'reservation': reservation})

@login_required
def reservation_update_status(request, pk, new_status):
    reservation = reservation_service.update_reservation_status(pk, new_status)
    return redirect('reservation_detail', pk=reservation.pk)

@login_required
def generate_ticket(request, reservation_pk):
    reservation = get_object_or_404(Reservation, pk=reservation_pk)
    if reservation.status not in ['CON', 'PAID']:
        return render(request, 'airline/reservation_error.html', {'message': 'Ticket can only be generated for confirmed or paid reservations.'})

    ticket = ticket_service.issue_ticket(reservation_pk)
    return _generate_ticket_pdf(ticket, reservation)

def _generate_ticket_pdf(ticket, reservation):
    html_string = render_to_string('airline/ticket_template.html', {'ticket': ticket, 'reservation': reservation})
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.barcode}.pdf"'
    return response

@login_required
def ticket_detail(request, pk):
    ticket = ticket_service.get_ticket_detail(pk)
    return render(request, 'airline/ticket_detail.html', {'ticket': ticket})

@login_required
def passenger_list_by_flight(request, flight_pk):
    flight, reservations = reservation_service.get_passengers_by_flight(flight_pk)
    context = {
        'flight': flight,
        'passengers': reservations,
    }
    return render(request, 'airline/passenger_list_by_flight.html', context)
