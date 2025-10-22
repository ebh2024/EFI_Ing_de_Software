from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from .forms import FlightForm, PassengerForm, AirplaneForm, SeatLayoutForm, SeatTypeForm, SeatLayoutPositionForm
from .models import Flight, Passenger, Airplane, SeatLayout, SeatType, SeatLayoutPosition

# Generic CRUD functions
def create_object(request, form_class, redirect_url, template_name, context_name):
    """
    Función genérica para crear un nuevo objeto usando un formulario.

    Maneja solicitudes GET para mostrar el formulario y POST para procesar la creación.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        form_class (Form): Clase del formulario a usar.
        redirect_url (str): URL para redirigir después de la creación exitosa.
        template_name (str): Nombre de la plantilla a renderizar.
        context_name (str): Nombre del contexto para el objeto en la plantilla.

    Retorna:
        HttpResponse: Respuesta renderizada con el formulario o redirección.
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class()
    return render(request, template_name, {'form': form, 'action': _('Create')})

def update_object(request, pk, model_class, form_class, redirect_url, template_name, context_name):
    """
    Función genérica para actualizar un objeto existente.

    Maneja solicitudes GET para mostrar el formulario con datos iniciales y POST para procesar la actualización.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del objeto a actualizar.
        model_class (Model): Clase del modelo del objeto.
        form_class (Form): Clase del formulario a usar.
        redirect_url (str): URL para redirigir después de la actualización exitosa.
        template_name (str): Nombre de la plantilla a renderizar.
        context_name (str): Nombre del contexto para el objeto en la plantilla.

    Retorna:
        HttpResponse: Respuesta renderizada con el formulario o redirección.
    """
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
    """
    Función genérica para eliminar un objeto.

    Maneja solicitudes GET para mostrar confirmación y POST para procesar la eliminación.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del objeto a eliminar.
        model_class (Model): Clase del modelo del objeto.
        redirect_url (str): URL para redirigir después de la eliminación.
        template_name (str): Nombre de la plantilla a renderizar.
        context_name (str): Nombre del contexto para el objeto en la plantilla.

    Retorna:
        HttpResponse: Respuesta renderizada con confirmación o redirección.
    """
    obj = get_object_or_404(model_class, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(redirect_url)
    return render(request, template_name, {context_name: obj})

# Flight CRUD Views
@login_required
def flight_list(request):
    """
    Vista para listar todos los vuelos.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta renderizada con la lista de vuelos.
    """
    flights = Flight.objects.all()
    return render(request, 'airline/flight_list.html', {'flights': flights})

@login_required
def flight_create(request):
    """
    Vista para crear un nuevo vuelo.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta de la función genérica create_object.
    """
    return create_object(request, FlightForm, 'flight_list', 'airline/flight_form.html', 'flight')

@login_required
def flight_update(request, pk):
    """
    Vista para actualizar un vuelo existente.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del vuelo.

    Retorna:
        HttpResponse: Respuesta de la función genérica update_object.
    """
    return update_object(request, pk, Flight, FlightForm, 'flight_list', 'airline/flight_form.html', 'flight')

@login_required
def flight_delete(request, pk):
    """
    Vista para eliminar un vuelo.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del vuelo.

    Retorna:
        HttpResponse: Respuesta de la función genérica delete_object.
    """
    return delete_object(request, pk, Flight, 'flight_list', 'airline/flight_confirm_delete.html', 'flight')

# Passenger CRUD Views
@login_required
def passenger_list(request):
    """
    Vista para listar todos los pasajeros.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta renderizada con la lista de pasajeros.
    """
    passengers = Passenger.objects.all()
    return render(request, 'airline/passenger_list.html', {'passengers': passengers})

@login_required
def passenger_create(request):
    """
    Vista para crear un nuevo pasajero.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta de la función genérica create_object.
    """
    return create_object(request, PassengerForm, 'passenger_list', 'airline/passenger_form.html', 'passenger')

@login_required
def passenger_update(request, pk):
    """
    Vista para actualizar un pasajero existente.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del pasajero.

    Retorna:
        HttpResponse: Respuesta de la función genérica update_object.
    """
    return update_object(request, pk, Passenger, PassengerForm, 'passenger_list', 'airline/passenger_form.html', 'passenger')

@login_required
def passenger_delete(request, pk):
    """
    Vista para eliminar un pasajero.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del pasajero.

    Retorna:
        HttpResponse: Respuesta renderizada con confirmación de eliminación.
    """
    passenger = get_object_or_404(Passenger, pk=pk)
    if request.method == 'POST':
        passenger.delete()
        return redirect('passenger_list')
    return render(request, 'airline/passenger_confirm_delete.html', {'passenger': passenger})

# Airplane CRUD Views
@login_required
def airplane_list(request):
    """
    Vista para listar todos los aviones.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta renderizada con la lista de aviones.
    """
    airplanes = Airplane.objects.all()
    return render(request, 'airline/airplane_list.html', {'airplanes': airplanes})

@login_required
def airplane_create(request):
    """
    Vista para crear un nuevo avión.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta de la función genérica create_object.
    """
    return create_object(request, AirplaneForm, 'airplane_list', 'airline/airplane_form.html', 'airplane')

@login_required
def airplane_update(request, pk):
    """
    Vista para actualizar un avión existente.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del avión.

    Retorna:
        HttpResponse: Respuesta de la función genérica update_object.
    """
    return update_object(request, pk, Airplane, AirplaneForm, 'airplane_list', 'airline/airplane_form.html', 'airplane')

@login_required
def airplane_delete(request, pk):
    """
    Vista para eliminar un avión.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del avión.

    Retorna:
        HttpResponse: Respuesta de la función genérica delete_object.
    """
    return delete_object(request, pk, Airplane, 'airplane_list', 'airline/airplane_confirm_delete.html', 'airplane')

# SeatLayout CRUD Views
@login_required
def seat_layout_list(request):
    """
    Vista para listar todos los layouts de asientos.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta renderizada con la lista de layouts de asientos.
    """
    seat_layouts = SeatLayout.objects.all()
    return render(request, 'airline/seat_layout_list.html', {'seat_layouts': seat_layouts})

@login_required
def seat_layout_create(request):
    """
    Vista para crear un nuevo layout de asientos.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta de la función genérica create_object.
    """
    return create_object(request, SeatLayoutForm, 'seat_layout_list', 'airline/seat_layout_form.html', 'seat_layout')

@login_required
def seat_layout_update(request, pk):
    """
    Vista para actualizar un layout de asientos existente.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del layout.

    Retorna:
        HttpResponse: Respuesta de la función genérica update_object.
    """
    return update_object(request, pk, SeatLayout, SeatLayoutForm, 'seat_layout_list', 'airline/seat_layout_form.html', 'seat_layout')

@login_required
def seat_layout_delete(request, pk):
    """
    Vista para eliminar un layout de asientos.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del layout.

    Retorna:
        HttpResponse: Respuesta de la función genérica delete_object.
    """
    return delete_object(request, pk, SeatLayout, 'seat_layout_list', 'airline/seat_layout_confirm_delete.html', 'seat_layout')

# SeatType CRUD Views
@login_required
def seat_type_list(request):
    """
    Vista para listar todos los tipos de asientos.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta renderizada con la lista de tipos de asientos.
    """
    seat_types = SeatType.objects.all()
    return render(request, 'airline/seat_type_list.html', {'seat_types': seat_types})

@login_required
def seat_type_create(request):
    """
    Vista para crear un nuevo tipo de asiento.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta de la función genérica create_object.
    """
    return create_object(request, SeatTypeForm, 'seat_type_list', 'airline/seat_type_form.html', 'seat_type')

@login_required
def seat_type_update(request, pk):
    """
    Vista para actualizar un tipo de asiento existente.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del tipo de asiento.

    Retorna:
        HttpResponse: Respuesta de la función genérica update_object.
    """
    return update_object(request, pk, SeatType, SeatTypeForm, 'seat_type_list', 'airline/seat_type_form.html', 'seat_type')

@login_required
def seat_type_delete(request, pk):
    """
    Vista para eliminar un tipo de asiento.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria del tipo de asiento.

    Retorna:
        HttpResponse: Respuesta de la función genérica delete_object.
    """
    return delete_object(request, pk, SeatType, 'seat_type_list', 'airline/seat_type_confirm_delete.html', 'seat_type')

# SeatLayoutPosition CRUD Views
@login_required
def seat_layout_position_list(request):
    """
    Vista para listar todas las posiciones de layouts de asientos.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta renderizada con la lista de posiciones de layouts.
    """
    seat_layout_positions = SeatLayoutPosition.objects.all()
    return render(request, 'airline/seat_layout_position_list.html', {'seat_layout_positions': seat_layout_positions})

@login_required
def seat_layout_position_create(request):
    """
    Vista para crear una nueva posición de layout de asientos.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.

    Retorna:
        HttpResponse: Respuesta de la función genérica create_object.
    """
    return create_object(request, SeatLayoutPositionForm, 'seat_layout_position_list', 'airline/seat_layout_position_form.html', 'seat_layout_position')

@login_required
def seat_layout_position_update(request, pk):
    """
    Vista para actualizar una posición de layout existente.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria de la posición.

    Retorna:
        HttpResponse: Respuesta de la función genérica update_object.
    """
    return update_object(request, pk, SeatLayoutPosition, SeatLayoutPositionForm, 'seat_layout_position_list', 'airline/seat_layout_position_form.html', 'seat_layout_position')

@login_required
def seat_layout_position_delete(request, pk):
    """
    Vista para eliminar una posición de layout de asientos.

    Requiere autenticación del usuario.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria de la posición.

    Retorna:
        HttpResponse: Respuesta de la función genérica delete_object.
    """
    return delete_object(request, pk, SeatLayoutPosition, 'seat_layout_position_list', 'airline/seat_layout_position_confirm_delete.html', 'seat_layout_position')
