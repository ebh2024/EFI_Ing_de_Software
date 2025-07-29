from django.shortcuts import render, get_object_or_404, redirect
from .models import Vuelo, Asiento, Reserva, Pasajero
from .forms import ReservaForm, PasajeroForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import secrets
import string

def lista_vuelos(request):
    vuelos = Vuelo.objects.all()
    return render(request, 'gestion/lista_vuelos.html', {'vuelos': vuelos})

def detalle_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    asientos = Asiento.objects.filter(vuelo=vuelo)
    return render(request, 'gestion/detalle_vuelo.html', {'vuelo': vuelo, 'asientos': asientos})

@login_required
def reservar_asiento(request, asiento_id):
    asiento = get_object_or_404(Asiento, pk=asiento_id)
    pasajero = get_object_or_404(Pasajero, user=request.user)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.vuelo = asiento.vuelo
            reserva.pasajero = pasajero
            reserva.asiento = asiento
            reserva.save()
            
            asiento.estado = 'reservado'
            asiento.save()
            
            return redirect('boleto', reserva_id=reserva.id)
    else:
        form = ReservaForm(initial={'vuelo': asiento.vuelo, 'pasajero': pasajero, 'asiento': asiento})

    return render(request, 'gestion/reservar_asiento.html', {'form': form, 'asiento': asiento})


@login_required
def boleto(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    return render(request, 'gestion/boleto.html', {'reserva': reserva})

def reporte_pasajeros_por_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    reservas = Reserva.objects.filter(vuelo=vuelo)
    return render(request, 'gestion/reporte_pasajeros.html', {'vuelo': vuelo, 'reservas': reservas})

def crear_pasajero(request):
    if request.method == 'POST':
        form = PasajeroForm(request.POST)
        if form.is_valid():
            # Crear un nuevo usuario
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
            )
            
            pasajero = form.save(commit=False)
            pasajero.user = user
            pasajero.save()
            return redirect('login')
    else:
        form = PasajeroForm()
    return render(request, 'gestion/crear_pasajero.html', {'form': form})
