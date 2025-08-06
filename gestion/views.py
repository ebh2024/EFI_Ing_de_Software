from django.shortcuts import render, redirect
from .forms import PassengerForm
from django.contrib.auth.decorators import login_required
from .services import FlightService, PassengerService, BookingService
from django.contrib import messages

def flight_list(request):
    flight_service = FlightService()
    flights = flight_service.get_all_flights()
    return render(request, 'gestion/flight_list.html', {'flights': flights})

def flight_detail(request, flight_id):
    flight_service = FlightService()
    flight, seats = flight_service.get_flight_details(flight_id)
    return render(request, 'gestion/flight_detail.html', {'flight': flight, 'seats': seats})

@login_required
def book_seat(request, seat_id):
    booking_service = BookingService()
    if request.method == 'POST':
        try:
            booking = booking_service.book_seat(seat_id, request.user)
            return redirect('ticket', booking_id=booking.id)
        except Exception as e:
            messages.error(request, str(e))
            seat = booking_service.seat_repository.get_by_id(seat_id)
            return redirect('flight_detail', flight_id=seat.flight.id)
    else:
        return render(request, 'gestion/book_seat.html', {'seat_id': seat_id})


@login_required
def ticket(request, booking_id):
    booking_service = BookingService()
    booking = booking_service.get_ticket(booking_id)
    return render(request, 'gestion/ticket.html', {'booking': booking})

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def passenger_report_by_flight(request, flight_id):
    flight_service = FlightService()
    flight, bookings = flight_service.get_passenger_report(flight_id)
    return render(request, 'gestion/passenger_report.html', {'flight': flight, 'bookings': bookings})

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
            return redirect('login')
    else:
        form = PassengerForm()
    return render(request, 'gestion/create_passenger.html', {'form': form})
