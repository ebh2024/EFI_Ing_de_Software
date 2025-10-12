from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, FlightForm, PassengerForm, ReservationForm, TicketForm, AirplaneForm, SeatLayoutForm, SeatTypeForm, SeatLayoutPositionForm
from .models import Flight, Passenger, FlightHistory, Seat, Reservation, Ticket, Airplane, SeatLayout, SeatType, SeatLayoutPosition
from django.db import transaction
from django.http import HttpResponse
import uuid
from django.template.loader import render_to_string
from weasyprint import HTML
from decimal import Decimal # Import Decimal
from django.db.models import Q

def home(request):
    flights = Flight.objects.all()
    return render(request, 'airline/home.html', {'flights': flights})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login') # Redirect to login page after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'airline/register.html', {'form': form})

@login_required
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'airline/flight_list.html', {'flights': flights})

@login_required
def flight_create(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flight_list')
    else:
        form = FlightForm()
    return render(request, 'airline/flight_form.html', {'form': form, 'action': 'Create'})

@login_required
def flight_update(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            return redirect('flight_list')
    else:
        form = FlightForm(instance=flight)
    return render(request, 'airline/flight_form.html', {'form': form, 'action': 'Update'})

@login_required
def flight_delete(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        flight.delete()
        return redirect('flight_list')
    return render(request, 'airline/flight_confirm_delete.html', {'flight': flight})

@login_required
def passenger_list(request):
    passengers = Passenger.objects.all()
    return render(request, 'airline/passenger_list.html', {'passengers': passengers})

@login_required
def passenger_create(request):
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('passenger_list')
    else:
        form = PassengerForm()
    return render(request, 'airline/passenger_form.html', {'form': form, 'action': 'Create'})

@login_required
def passenger_update(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    if request.method == 'POST':
        form = PassengerForm(request.POST, instance=passenger)
        if form.is_valid():
            form.save()
            return redirect('passenger_list')
    else:
        form = PassengerForm(instance=passenger)
    return render(request, 'airline/passenger_form.html', {'form': form, 'action': 'Update'})

@login_required
def passenger_delete(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    if request.method == 'POST':
        passenger.delete()
        return redirect('passenger_list')
    return render(request, 'airline/passenger_confirm_delete.html', {'passenger': passenger})

@login_required
def passenger_flight_history(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    flight_history = FlightHistory.objects.filter(passenger=passenger).order_by('-booking_date')
    return render(request, 'airline/passenger_flight_history.html', {'passenger': passenger, 'flight_history': flight_history})

# Airplane CRUD Views
@login_required
def airplane_list(request):
    airplanes = Airplane.objects.all()
    return render(request, 'airline/airplane_list.html', {'airplanes': airplanes})

@login_required
def airplane_create(request):
    if request.method == 'POST':
        form = AirplaneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('airplane_list')
    else:
        form = AirplaneForm()
    return render(request, 'airline/airplane_form.html', {'form': form, 'action': 'Create'})

@login_required
def airplane_update(request, pk):
    airplane = get_object_or_404(Airplane, pk=pk)
    if request.method == 'POST':
        form = AirplaneForm(request.POST, instance=airplane)
        if form.is_valid():
            form.save()
            return redirect('airplane_list')
    else:
        form = AirplaneForm(instance=airplane)
    return render(request, 'airline/airplane_form.html', {'form': form, 'action': 'Update'})

@login_required
def airplane_delete(request, pk):
    airplane = get_object_or_404(Airplane, pk=pk)
    if request.method == 'POST':
        airplane.delete()
        return redirect('airplane_list')
    return render(request, 'airline/airplane_confirm_delete.html', {'airplane': airplane})

# SeatLayout CRUD Views
@login_required
def seat_layout_list(request):
    seat_layouts = SeatLayout.objects.all()
    return render(request, 'airline/seat_layout_list.html', {'seat_layouts': seat_layouts})

@login_required
def seat_layout_create(request):
    if request.method == 'POST':
        form = SeatLayoutForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seat_layout_list')
    else:
        form = SeatLayoutForm()
    return render(request, 'airline/seat_layout_form.html', {'form': form, 'action': 'Create'})

@login_required
def seat_layout_update(request, pk):
    seat_layout = get_object_or_404(SeatLayout, pk=pk)
    if request.method == 'POST':
        form = SeatLayoutForm(request.POST, instance=seat_layout)
        if form.is_valid():
            form.save()
            return redirect('seat_layout_list')
    else:
        form = SeatLayoutForm(instance=seat_layout)
    return render(request, 'airline/seat_layout_form.html', {'form': form, 'action': 'Update'})

@login_required
def seat_layout_delete(request, pk):
    seat_layout = get_object_or_404(SeatLayout, pk=pk)
    if request.method == 'POST':
        seat_layout.delete()
        return redirect('seat_layout_list')
    return render(request, 'airline/seat_layout_confirm_delete.html', {'seat_layout': seat_layout})

# SeatType CRUD Views
@login_required
def seat_type_list(request):
    seat_types = SeatType.objects.all()
    return render(request, 'airline/seat_type_list.html', {'seat_types': seat_types})

@login_required
def seat_type_create(request):
    if request.method == 'POST':
        form = SeatTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seat_type_list')
    else:
        form = SeatTypeForm()
    return render(request, 'airline/seat_type_form.html', {'form': form, 'action': 'Create'})

@login_required
def seat_type_update(request, pk):
    seat_type = get_object_or_404(SeatType, pk=pk)
    if request.method == 'POST':
        form = SeatTypeForm(request.POST, instance=seat_type)
        if form.is_valid():
            form.save()
            return redirect('seat_type_list')
    else:
        form = SeatTypeForm(instance=seat_type)
    return render(request, 'airline/seat_type_form.html', {'form': form, 'action': 'Update'})

@login_required
def seat_type_delete(request, pk):
    seat_type = get_object_or_404(SeatType, pk=pk)
    if request.method == 'POST':
        seat_type.delete()
        return redirect('seat_type_list')
    return render(request, 'airline/seat_type_confirm_delete.html', {'seat_type': seat_type})

# SeatLayoutPosition CRUD Views
@login_required
def seat_layout_position_list(request):
    seat_layout_positions = SeatLayoutPosition.objects.all()
    return render(request, 'airline/seat_layout_position_list.html', {'seat_layout_positions': seat_layout_positions})

@login_required
def seat_layout_position_create(request):
    if request.method == 'POST':
        form = SeatLayoutPositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seat_layout_position_list')
    else:
        form = SeatLayoutPositionForm()
    return render(request, 'airline/seat_layout_position_form.html', {'form': form, 'action': 'Create'})

@login_required
def seat_layout_position_update(request, pk):
    seat_layout_position = get_object_or_404(SeatLayoutPosition, pk=pk)
    if request.method == 'POST':
        form = SeatLayoutPositionForm(request.POST, instance=seat_layout_position)
        if form.is_valid():
            form.save()
            return redirect('seat_layout_position_list')
    else:
        form = SeatLayoutPositionForm(instance=seat_layout_position)
    return render(request, 'airline/seat_layout_position_form.html', {'form': form, 'action': 'Update'})

@login_required
def seat_layout_position_delete(request, pk):
    seat_layout_position = get_object_or_404(SeatLayoutPosition, pk=pk)
    if request.method == 'POST':
        seat_layout_position.delete()
        return redirect('seat_layout_position_list')
    return render(request, 'airline/seat_layout_position_confirm_delete.html', {'seat_layout_position': seat_layout_position})

@login_required
def flight_detail_with_seats(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    # Get all seats for the airplane associated with the flight
    seats = Seat.objects.filter(airplane=flight.airplane).order_by('row', 'column')
    
    # Get reserved seats for this specific flight
    reserved_seats_ids = Reservation.objects.filter(flight=flight, status__in=['PEN', 'CON', 'PAID']).values_list('seat__id', flat=True)
    
    # Mark seats as available or reserved
    for seat in seats:
        seat.is_reserved = seat.id in reserved_seats_ids
    
    # Group seats by row for easier template rendering
    seats_by_row = {}
    for seat in seats:
        seats_by_row.setdefault(seat.row, []).append(seat)

    return render(request, 'airline/flight_detail_with_seats.html', {
        'flight': flight,
        'seats_by_row': dict(sorted(seats_by_row.items())),
    })

@login_required
def reserve_seat(request, flight_pk, seat_pk):
    flight = get_object_or_404(Flight, pk=flight_pk)
    seat = get_object_or_404(Seat, pk=seat_pk)

    # Check if the seat is already reserved for this flight
    if Reservation.objects.filter(flight=flight, seat=seat, status__in=['PEN', 'CON', 'PAID']).exists():
        return render(request, 'airline/reservation_error.html', {'message': 'This seat is already reserved for this flight.'})

    # For simplicity, let's assume the logged-in user is the passenger.
    # In a real application, you'd link User to Passenger or create a new Passenger.
    # For now, let's create a dummy passenger if none exists for the current user.
    # This part needs to be refined based on actual user/passenger management.
    passenger, created = Passenger.objects.get_or_create(
        email=request.user.email,
        defaults={'first_name': request.user.first_name if request.user.first_name else request.user.username,
                  'last_name': request.user.last_name if request.user.last_name else '',
                  'document_number': str(uuid.uuid4())[:10], # Dummy document number
                  'date_of_birth': '2000-01-01'} # Dummy date of birth
    )
    # If the user is not a superuser, ensure they are linked to a passenger profile
    if not request.user.is_superuser and not hasattr(request.user, 'passenger_profile'):
        # Assuming a one-to-one link or a way to associate User with Passenger
        # For now, we'll just use the dummy passenger created above.
        pass # Further logic to link user to passenger if needed

    if request.method == 'POST':
        form = ReservationForm(request.POST, initial={'flight': flight}) # Pass flight in initial for seat queryset filtering
        if form.is_valid():
            with transaction.atomic():
                reservation = form.save(commit=False)
                reservation.flight = flight
                reservation.seat = seat
                reservation.passenger = passenger # Assign the passenger
                reservation.status = 'PEN' # Initial status
                
                # Calculate price based on seat type and flight base price
                seat_price_multiplier = Decimal('1.0') # Use Decimal for calculations
                if seat.seat_type and seat.seat_type.code == 'PRE': # Assuming 'PRE' is a code for Premium
                    seat_price_multiplier = seat.seat_type.price_multiplier
                elif seat.seat_type and seat.seat_type.code == 'EXE': # Assuming 'EXE' is a code for Executive
                    seat_price_multiplier = seat.seat_type.price_multiplier
                elif seat.seat_type: # Default to seat_type's multiplier if it exists
                    seat_price_multiplier = seat.seat_type.price_multiplier
                
                reservation.price = flight.base_price * seat_price_multiplier
                
                reservation.reservation_code = str(uuid.uuid4()).replace('-', '')[:20] # Generate unique code
                reservation.save()

                # Update seat status
                seat.status = 'Reserved'
                seat.save()

                return redirect('reservation_detail', pk=reservation.pk)
        else:
            # If form is not valid, render with errors
            print(form.errors) # Add debug print for form errors
            return render(request, 'airline/reserve_seat.html', {
                'form': form,
                'flight': flight,
                'seat': seat,
                'passenger': passenger,
                'action': 'Reserve'
            })
    else:
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
    reservations = Reservation.objects.all().order_by('-reservation_date')
    return render(request, 'airline/reservation_list.html', {'reservations': reservations})

@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    return render(request, 'airline/reservation_detail.html', {'reservation': reservation})

@login_required
def reservation_update_status(request, pk, new_status):
    reservation = get_object_or_404(Reservation, pk=pk)
    if new_status in [choice[0] for choice in Reservation.RESERVATION_STATUS_CHOICES]:
        reservation.status = new_status
        reservation.save() # The save method in the model will update seat status
    return redirect('reservation_detail', pk=reservation.pk)

@login_required
def generate_ticket(request, reservation_pk):
    reservation = get_object_or_404(Reservation, pk=reservation_pk)
    if reservation.status not in ['CON', 'PAID']:
        return render(request, 'airline/reservation_error.html', {'message': 'Ticket can only be generated for confirmed or paid reservations.'})

    ticket, created = Ticket.objects.get_or_create(
        reservation=reservation,
        defaults={
            'barcode': str(uuid.uuid4()).replace('-', '')[:20],
            'status': 'EMI'
        }
    )
    
    # Render the ticket as HTML
    html_string = render_to_string('airline/ticket_template.html', {'ticket': ticket, 'reservation': reservation})
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.barcode}.pdf"'
    return response

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    return render(request, 'airline/ticket_detail.html', {'ticket': ticket})

@login_required
def passenger_list_by_flight(request, flight_pk):
    flight = get_object_or_404(Flight, pk=flight_pk)
    reservations = Reservation.objects.filter(flight=flight).select_related('passenger', 'seat').order_by('passenger__last_name', 'passenger__first_name')
    
    context = {
        'flight': flight,
        'passengers': reservations,
    }
    return render(request, 'airline/passenger_list_by_flight.html', context)
