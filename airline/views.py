from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, FlightForm
from .models import Flight

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
