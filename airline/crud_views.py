from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from .forms import FlightForm, PassengerForm, AirplaneForm, SeatLayoutForm, SeatTypeForm, SeatLayoutPositionForm
from .models import Flight, Passenger, Airplane, SeatLayout, SeatType, SeatLayoutPosition

# Generic CRUD functions
def create_object(request, form_class, redirect_url, template_name, context_name):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class()
    return render(request, template_name, {'form': form, 'action': _('Create')})

def update_object(request, pk, model_class, form_class, redirect_url, template_name, context_name):
    obj = get_object_or_404(model_class, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class(instance=obj)
    return render(request, template_name, {'form': form, 'action': _('Update'), context_name: obj})

def delete_object(request, pk, model_class, redirect_url, template_name, context_name):
    obj = get_object_or_404(model_class, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(redirect_url)
    return render(request, template_name, {context_name: obj})

# Flight CRUD Views
@login_required
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'airline/flight_list.html', {'flights': flights})

@login_required
def flight_create(request):
    return create_object(request, FlightForm, 'flight_list', 'airline/flight_form.html', 'flight')

@login_required
def flight_update(request, pk):
    return update_object(request, pk, Flight, FlightForm, 'flight_list', 'airline/flight_form.html', 'flight')

@login_required
def flight_delete(request, pk):
    return delete_object(request, pk, Flight, 'flight_list', 'airline/flight_confirm_delete.html', 'flight')

# Passenger CRUD Views
@login_required
def passenger_list(request):
    passengers = Passenger.objects.all()
    return render(request, 'airline/passenger_list.html', {'passengers': passengers})

@login_required
def passenger_create(request):
    return create_object(request, PassengerForm, 'passenger_list', 'airline/passenger_form.html', 'passenger')

@login_required
def passenger_update(request, pk):
    return update_object(request, pk, Passenger, PassengerForm, 'passenger_list', 'airline/passenger_form.html', 'passenger')

@login_required
def passenger_delete(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    if request.method == 'POST':
        passenger.delete()
        return redirect('passenger_list')
    return render(request, 'airline/passenger_confirm_delete.html', {'passenger': passenger})

# Airplane CRUD Views
@login_required
def airplane_list(request):
    airplanes = Airplane.objects.all()
    return render(request, 'airline/airplane_list.html', {'airplanes': airplanes})

@login_required
def airplane_create(request):
    return create_object(request, AirplaneForm, 'airplane_list', 'airline/airplane_form.html', 'airplane')

@login_required
def airplane_update(request, pk):
    return update_object(request, pk, Airplane, AirplaneForm, 'airplane_list', 'airline/airplane_form.html', 'airplane')

@login_required
def airplane_delete(request, pk):
    return delete_object(request, pk, Airplane, 'airplane_list', 'airline/airplane_confirm_delete.html', 'airplane')

# SeatLayout CRUD Views
@login_required
def seat_layout_list(request):
    seat_layouts = SeatLayout.objects.all()
    return render(request, 'airline/seat_layout_list.html', {'seat_layouts': seat_layouts})

@login_required
def seat_layout_create(request):
    return create_object(request, SeatLayoutForm, 'seat_layout_list', 'airline/seat_layout_form.html', 'seat_layout')

@login_required
def seat_layout_update(request, pk):
    return update_object(request, pk, SeatLayout, SeatLayoutForm, 'seat_layout_list', 'airline/seat_layout_form.html', 'seat_layout')

@login_required
def seat_layout_delete(request, pk):
    return delete_object(request, pk, SeatLayout, 'seat_layout_list', 'airline/seat_layout_confirm_delete.html', 'seat_layout')

# SeatType CRUD Views
@login_required
def seat_type_list(request):
    seat_types = SeatType.objects.all()
    return render(request, 'airline/seat_type_list.html', {'seat_types': seat_types})

@login_required
def seat_type_create(request):
    return create_object(request, SeatTypeForm, 'seat_type_list', 'airline/seat_type_form.html', 'seat_type')

@login_required
def seat_type_update(request, pk):
    return update_object(request, pk, SeatType, SeatTypeForm, 'seat_type_list', 'airline/seat_type_form.html', 'seat_type')

@login_required
def seat_type_delete(request, pk):
    return delete_object(request, pk, SeatType, 'seat_type_list', 'airline/seat_type_confirm_delete.html', 'seat_type')

# SeatLayoutPosition CRUD Views
@login_required
def seat_layout_position_list(request):
    seat_layout_positions = SeatLayoutPosition.objects.all()
    return render(request, 'airline/seat_layout_position_list.html', {'seat_layout_positions': seat_layout_positions})

@login_required
def seat_layout_position_create(request):
    return create_object(request, SeatLayoutPositionForm, 'seat_layout_position_list', 'airline/seat_layout_position_form.html', 'seat_layout_position')

@login_required
def seat_layout_position_update(request, pk):
    return update_object(request, pk, SeatLayoutPosition, SeatLayoutPositionForm, 'seat_layout_position_list', 'airline/seat_layout_position_form.html', 'seat_layout_position')

@login_required
def seat_layout_position_delete(request, pk):
    return delete_object(request, pk, SeatLayoutPosition, 'seat_layout_position_list', 'airline/seat_layout_position_confirm_delete.html', 'seat_layout_position')
