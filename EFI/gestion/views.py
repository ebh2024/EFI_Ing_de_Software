from django.shortcuts import render, redirect
from .forms import ReservaForm, PasajeroForm
from django.contrib.auth.decorators import login_required
from .services import VueloService, PasajeroService, ReservaService

def lista_vuelos(request):
    vuelo_service = VueloService()
    vuelos = vuelo_service.get_all_vuelos()
    return render(request, 'gestion/lista_vuelos.html', {'vuelos': vuelos})

def detalle_vuelo(request, vuelo_id):
    vuelo_service = VueloService()
    vuelo, asientos = vuelo_service.get_vuelo_details(vuelo_id)
    return render(request, 'gestion/detalle_vuelo.html', {'vuelo': vuelo, 'asientos': asientos})

@login_required
def reservar_asiento(request, asiento_id):
    reserva_service = ReservaService()
    if request.method == 'POST':
        try:
            reserva = reserva_service.reservar_asiento(asiento_id, request.user)
            return redirect('boleto', reserva_id=reserva.id)
        except Exception as e:
            # Manejar el error, por ejemplo, mostrando un mensaje al usuario
            return redirect('detalle_vuelo', vuelo_id=reserva_service.asiento_repository.get_by_id(asiento_id).vuelo.id)
    else:
        # La vista de reserva ahora es más simple y no necesita un formulario
        return render(request, 'gestion/reservar_asiento.html', {'asiento_id': asiento_id})


@login_required
def boleto(request, reserva_id):
    reserva_service = ReservaService()
    reserva = reserva_service.get_boleto(reserva_id)
    return render(request, 'gestion/boleto.html', {'reserva': reserva})

def reporte_pasajeros_por_vuelo(request, vuelo_id):
    vuelo_service = VueloService()
    vuelo, reservas = vuelo_service.get_reporte_pasajeros(vuelo_id)
    return render(request, 'gestion/reporte_pasajeros.html', {'vuelo': vuelo, 'reservas': reservas})

def crear_pasajero(request):
    if request.method == 'POST':
        form = PasajeroForm(request.POST)
        if form.is_valid():
            pasajero_service = PasajeroService()
            pasajero_service.create_pasajero(
                form.cleaned_data['nombre'],
                form.cleaned_data['apellido'],
                form.cleaned_data['documento'],
                form.cleaned_data['email'],
                form.cleaned_data['telefono']
            )
            return redirect('login')
    else:
        form = PasajeroForm()
    return render(request, 'gestion/crear_pasajero.html', {'form': form})
