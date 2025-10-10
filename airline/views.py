from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, FlightForm, PassengerForm
from .models import Flight, Passenger, FlightHistory

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
