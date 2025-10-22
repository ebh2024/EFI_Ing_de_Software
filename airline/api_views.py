from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .models import Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket
from .serializers import AirplaneSerializer, FlightSerializer, PassengerSerializer, ReservationSerializer, SeatLayoutSerializer, SeatTypeSerializer, SeatLayoutPositionSerializer, FlightHistorySerializer, TicketSerializer, SeatSerializer
from .services import (
    AirplaneService, FlightService, PassengerService, ReservationService,
    SeatLayoutService, SeatTypeService, SeatLayoutPositionService, TicketService, FlightHistoryService
)
from .repositories import SeatRepository
from .mixins import ServiceActionMixin

class AirplaneViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar aviones a través de la API REST.

    Proporciona operaciones CRUD para aviones, incluyendo creación con asientos.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todos los aviones.
        serializer_class: Serializador para aviones.
        service: Servicio para lógica de negocio de aviones.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    service = AirplaneService()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo avión con sus asientos.

        Parámetros:
            request (Request): Solicitud HTTP con datos del avión.

        Retorna:
            Response: Respuesta con datos del avión creado.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_airplane_with_seats')

    def update(self, request, *args, **kwargs):
        """
        Actualiza un avión existente.

        Parámetros:
            request (Request): Solicitud HTTP con datos actualizados.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave, incluyendo 'partial' para actualizaciones parciales.

        Retorna:
            Response: Respuesta con datos del avión actualizado.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_airplane')

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un avión.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Respuesta confirmando la eliminación.
        """
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_airplane')

class FlightViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar vuelos a través de la API REST.

    Proporciona operaciones CRUD para vuelos, incluyendo consulta de asientos disponibles.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todos los vuelos.
        serializer_class: Serializador para vuelos.
        service: Servicio para lógica de negocio de vuelos.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    service = FlightService()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo vuelo.

        Parámetros:
            request (Request): Solicitud HTTP con datos del vuelo.

        Retorna:
            Response: Respuesta con datos del vuelo creado.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_flight')

    def update(self, request, *args, **kwargs):
        """
        Actualiza un vuelo existente.

        Parámetros:
            request (Request): Solicitud HTTP con datos actualizados.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave, incluyendo 'partial' para actualizaciones parciales.

        Retorna:
            Response: Respuesta con datos del vuelo actualizado.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_flight')

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un vuelo.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Respuesta confirmando la eliminación.
        """
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_flight')

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """
        Acción personalizada para obtener asientos disponibles en un vuelo.

        Parámetros:
            request (Request): Solicitud HTTP.
            pk (int): Clave primaria del vuelo.

        Retorna:
            Response: Lista de asientos disponibles o error.
        """
        try:
            available_seats = self.service.get_available_seats(pk)
            serializer = SeatSerializer(available_seats, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PassengerViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar pasajeros a través de la API REST.

    Proporciona operaciones CRUD para pasajeros.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todos los pasajeros.
        serializer_class: Serializador para pasajeros.
        service: Servicio para lógica de negocio de pasajeros.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    service = PassengerService()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo pasajero.

        Parámetros:
            request (Request): Solicitud HTTP con datos del pasajero.

        Retorna:
            Response: Respuesta con datos del pasajero creado.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_passenger')

    def update(self, request, *args, **kwargs):
        """
        Actualiza un pasajero existente.

        Parámetros:
            request (Request): Solicitud HTTP con datos actualizados.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave, incluyendo 'partial' para actualizaciones parciales.

        Retorna:
            Response: Respuesta con datos del pasajero actualizado.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_passenger')

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un pasajero.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Respuesta confirmando la eliminación.
        """
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_passenger')

class ReservationViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar reservas a través de la API REST.

    Proporciona operaciones CRUD para reservas, incluyendo confirmación y cancelación.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todas las reservas.
        serializer_class: Serializador para reservas.
        service: Servicio para lógica de negocio de reservas.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    service = ReservationService()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crea una nueva reserva.

        Parámetros:
            request (Request): Solicitud HTTP con datos de la reserva.

        Retorna:
            Response: Respuesta con datos de la reserva creada o error de validación.
        """
        try:
            flight_id, passenger_id, seat_id, price = self._get_reservation_creation_data(request.data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

        def _create_reservation():
            reservation = self.service.create_reservation(flight_id, passenger_id, seat_id, price)
            return Response(self.get_serializer(reservation).data, status=status.HTTP_201_CREATED)
        return self._handle_service_action(_create_reservation)

    def _get_reservation_creation_data(self, data):
        """
        Extrae y valida los datos necesarios para crear una reserva.

        Parámetros:
            data (dict): Datos de la solicitud.

        Retorna:
            tuple: flight_id, passenger_id, seat_id, price.

        Raises:
            ValidationError: Si faltan campos requeridos.
        """
        flight_id = data.get('flight')
        passenger_id = data.get('passenger')
        seat_id = data.get('seat')
        price = data.get('price')

        if not all([flight_id, passenger_id, seat_id, price]):
            raise ValidationError('Missing required fields: flight, passenger, seat, price')
        return flight_id, passenger_id, seat_id, price

    def update(self, request, *args, **kwargs):
        """
        Actualiza una reserva existente.

        Parámetros:
            request (Request): Solicitud HTTP con datos actualizados.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave, incluyendo 'partial' para actualizaciones parciales.

        Retorna:
            Response: Respuesta con datos de la reserva actualizada.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_reservation')

    def destroy(self, request, *args, **kwargs):
        """
        Elimina una reserva.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Respuesta confirmando la eliminación.
        """
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_reservation')

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Acción para confirmar una reserva.

        Parámetros:
            request (Request): Solicitud HTTP.
            pk (int): Clave primaria de la reserva.

        Retorna:
            Response: Datos de la reserva confirmada.
        """
        def _confirm():
            reservation = self.service.confirm_reservation(pk)
            return Response(self.get_serializer(reservation).data)
        return self._handle_service_action(_confirm)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Acción para cancelar una reserva.

        Parámetros:
            request (Request): Solicitud HTTP.
            pk (int): Clave primaria de la reserva.

        Retorna:
            Response: Datos de la reserva cancelada.
        """
        def _cancel():
            reservation = self.service.cancel_reservation(pk)
            return Response(self.get_serializer(reservation).data)
        return self._handle_service_action(_cancel)

class SeatLayoutViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar layouts de asientos a través de la API REST.

    Proporciona operaciones CRUD para layouts de asientos, incluyendo creación con posiciones.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todos los layouts de asientos.
        serializer_class: Serializador para layouts de asientos.
        service: Servicio para lógica de negocio de layouts de asientos.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = SeatLayout.objects.all()
    serializer_class = SeatLayoutSerializer
    service = SeatLayoutService()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo layout de asientos con posiciones.

        Parámetros:
            request (Request): Solicitud HTTP con datos del layout.

        Retorna:
            Response: Respuesta con datos del layout creado o error de validación.
        """
        try:
            layout_name, rows, columns, positions_data = self._get_seat_layout_creation_data(request.data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

        def _create_seat_layout():
            seat_layout = self.service.create_seat_layout_with_positions(layout_name, rows, columns, positions_data)
            return Response(self.get_serializer(seat_layout).data, status=status.HTTP_201_CREATED)
        return self._handle_service_action(_create_seat_layout)

    def _get_seat_layout_creation_data(self, data):
        """
        Extrae y valida los datos necesarios para crear un layout de asientos.

        Parámetros:
            data (dict): Datos de la solicitud.

        Retorna:
            tuple: layout_name, rows, columns, positions_data.

        Raises:
            ValidationError: Si faltan campos requeridos.
        """
        layout_name = data.get('layout_name')
        rows = data.get('rows')
        columns = data.get('columns')
        positions_data = data.get('positions', [])

        if not all([layout_name, rows, columns]):
            raise ValidationError('Missing required fields: layout_name, rows, columns')
        return layout_name, rows, columns, positions_data

    def update(self, request, *args, **kwargs):
        """
        Actualiza un layout de asientos existente.

        Parámetros:
            request (Request): Solicitud HTTP con datos actualizados.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave, incluyendo 'partial' para actualizaciones parciales.

        Retorna:
            Response: Respuesta con datos del layout actualizado.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_seat_layout')

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un layout de asientos.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Respuesta confirmando la eliminación.
        """
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_seat_layout')

class SeatTypeViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar tipos de asientos a través de la API REST.

    Proporciona operaciones CRUD para tipos de asientos.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todos los tipos de asientos.
        serializer_class: Serializador para tipos de asientos.
        service: Servicio para lógica de negocio de tipos de asientos.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer
    service = SeatTypeService()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo tipo de asiento.

        Parámetros:
            request (Request): Solicitud HTTP con datos del tipo de asiento.

        Retorna:
            Response: Respuesta con datos del tipo de asiento creado.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_seat_type')

    def update(self, request, *args, **kwargs):
        """
        Actualiza un tipo de asiento existente.

        Parámetros:
            request (Request): Solicitud HTTP con datos actualizados.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave, incluyendo 'partial' para actualizaciones parciales.

        Retorna:
            Response: Respuesta con datos del tipo de asiento actualizado.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_seat_type')

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un tipo de asiento.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Respuesta confirmando la eliminación.
        """
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_seat_type')

class SeatLayoutPositionViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar posiciones de layouts de asientos a través de la API REST.

    Proporciona operaciones CRUD para posiciones de asientos en layouts.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todas las posiciones de layouts.
        serializer_class: Serializador para posiciones de layouts.
        service: Servicio para lógica de negocio de posiciones de layouts.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = SeatLayoutPosition.objects.all()
    serializer_class = SeatLayoutPositionSerializer
    service = SeatLayoutPositionService()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crea una nueva posición en un layout de asientos.

        Parámetros:
            request (Request): Solicitud HTTP con datos de la posición.

        Retorna:
            Response: Respuesta con datos de la posición creada.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_seat_layout_position')

    def update(self, request, *args, **kwargs):
        """
        Actualiza una posición de layout existente.

        Parámetros:
            request (Request): Solicitud HTTP con datos actualizados.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave, incluyendo 'partial' para actualizaciones parciales.

        Retorna:
            Response: Respuesta con datos de la posición actualizada.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_seat_layout_position')

    def destroy(self, request, *args, **kwargs):
        """
        Elimina una posición de layout de asientos.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Respuesta confirmando la eliminación.
        """
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_seat_layout_position')

class FlightHistoryViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar historial de vuelos a través de la API REST.

    Proporciona operaciones para consultar historial de vuelos por pasajero o vuelo.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todo el historial de vuelos.
        serializer_class: Serializador para historial de vuelos.
        service: Servicio para lógica de negocio de historial de vuelos.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = FlightHistory.objects.all()
    serializer_class = FlightHistorySerializer
    service = FlightHistoryService()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Lista todo el historial de vuelos.

        Parámetros:
            request (Request): Solicitud HTTP.

        Retorna:
            Response: Lista de historial de vuelos.
        """
        flight_history = self.service.flight_history_repo.get_all()
        serializer = self.get_serializer(flight_history, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Recupera un registro específico del historial de vuelos.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Datos del registro de historial.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_passenger(self, request):
        """
        Acción para obtener historial de vuelos por pasajero.

        Parámetros:
            request (Request): Solicitud HTTP con query param 'passenger_id'.

        Retorna:
            Response: Lista de historial de vuelos del pasajero o error si falta ID.
        """
        passenger_id = request.query_params.get('passenger_id')
        if not passenger_id:
            return Response({'detail': 'Passenger ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        def _by_passenger():
            flight_history = self.service.get_flight_history_by_passenger(passenger_id)
            serializer = self.get_serializer(flight_history, many=True)
            return Response(serializer.data)
        return self._handle_service_action(_by_passenger)

    @action(detail=False, methods=['get'])
    def by_flight(self, request):
        """
        Acción para obtener historial de vuelos por vuelo.

        Parámetros:
            request (Request): Solicitud HTTP con query param 'flight_id'.

        Retorna:
            Response: Lista de historial de vuelos del vuelo o error si falta ID.
        """
        flight_id = request.query_params.get('flight_id')
        if not flight_id:
            return Response({'detail': 'Flight ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        def _by_flight():
            flight_history = self.service.get_flight_history_by_flight(flight_id)
            serializer = self.get_serializer(flight_history, many=True)
            return Response(serializer.data)
        return self._handle_service_action(_by_flight)

class TicketViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar tickets a través de la API REST.

    Proporciona operaciones para listar, recuperar y emitir/cancelar tickets.
    Requiere autenticación.

    Atributos:
        queryset: Conjunto de consultas para todos los tickets.
        serializer_class: Serializador para tickets.
        service: Servicio para lógica de negocio de tickets.
        permission_classes: Requiere autenticación de usuario.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    service = TicketService()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Lista todos los tickets.

        Parámetros:
            request (Request): Solicitud HTTP.

        Retorna:
            Response: Lista de tickets.
        """
        tickets = self.service.ticket_repo.get_all()
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Recupera un ticket específico.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Datos del ticket.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un ticket.

        Parámetros:
            request (Request): Solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos de palabra clave.

        Retorna:
            Response: Respuesta confirmando la eliminación.
        """
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_ticket')

    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None): # pk here is reservation_id
        """
        Acción para emitir un ticket a partir de una reserva.

        Parámetros:
            request (Request): Solicitud HTTP.
            pk (int): Clave primaria de la reserva.

        Retorna:
            Response: Datos del ticket emitido.
        """
        def _issue():
            ticket = self.service.issue_ticket(pk)
            return Response(self.get_serializer(ticket).data, status=status.HTTP_201_CREATED)
        return self._handle_service_action(_issue)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None): # pk here is ticket_id
        """
        Acción para cancelar un ticket.

        Parámetros:
            request (Request): Solicitud HTTP.
            pk (int): Clave primaria del ticket.

        Retorna:
            Response: Datos del ticket cancelado.
        """
        def _cancel():
            ticket = self.service.cancel_ticket(pk)
            return Response(self.get_serializer(ticket).data)
        return self._handle_service_action(_cancel)
