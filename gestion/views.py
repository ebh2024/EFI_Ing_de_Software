from django.shortcuts import render, get_object_or_404, redirect
from .models import Vuelo, Asiento, Reserva, Pasajero
from django.contrib.auth.decorators import login_required

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
    if asiento.estado == 'disponible':
        asiento.estado = 'reservado'
        asiento.save()
        pasajero = Pasajero.objects.get(user=request.user)
        reserva = Reserva.objects.create(vuelo=asiento.vuelo, pasajero=pasajero, asiento=asiento)
        return redirect('boleto', reserva_id=reserva.id)
    else:
        # Manejar el caso en que el asiento no está disponible
        return redirect('detalle_vuelo', vuelo_id=asiento.vuelo.id)

@login_required
def boleto(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    return render(request, 'gestion/boleto.html', {'reserva': reserva})

def reporte_pasajeros_por_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    reservas = Reserva.objects.filter(vuelo=vuelo)
    return render(request, 'gestion/reporte_pasajeros.html', {'vuelo': vuelo, 'reservas': reservas})
