from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from .models import Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket
from .serializers import AirplaneSerializer, FlightSerializer, PassengerSerializer, ReservationSerializer, SeatLayoutSerializer, SeatTypeSerializer, SeatLayoutPositionSerializer, FlightHistorySerializer, TicketSerializer, SeatSerializer
from .services import (
    AirplaneService, FlightService, PassengerService, ReservationService,
    SeatLayoutService, SeatTypeService, TicketService, FlightHistoryService
)
from .repositories import SeatRepository
from .mixins import ServiceActionMixin

class AirplaneViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    service = AirplaneService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_airplane_with_seats')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_airplane')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_airplane')

class FlightViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    service = FlightService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_flight')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_flight')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_flight')

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        try:
            available_seats = self.service.get_available_seats(pk)
            serializer = SeatSerializer(available_seats, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PassengerViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    service = PassengerService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_passenger')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_passenger')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_passenger')

class ReservationViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    service = ReservationService()

    def create(self, request, *args, **kwargs):
        flight_id = request.data.get('flight')
        passenger_id = request.data.get('passenger')
        seat_id = request.data.get('seat')
        price = request.data.get('price')

        if not all([flight_id, passenger_id, seat_id, price]):
            return Response({'detail': 'Missing required fields: flight, passenger, seat, price'}, status=status.HTTP_400_BAD_REQUEST)

        def _create_reservation():
            reservation = self.service.create_reservation(flight_id, passenger_id, seat_id, price)
            return Response(self.get_serializer(reservation).data, status=status.HTTP_201_CREATED)
        return self._handle_service_action(_create_reservation)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_reservation')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_reservation')

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        def _confirm():
            reservation = self.service.confirm_reservation(pk)
            return Response(self.get_serializer(reservation).data)
        return self._handle_service_action(_confirm)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        def _cancel():
            reservation = self.service.cancel_reservation(pk)
            return Response(self.get_serializer(reservation).data)
        return self._handle_service_action(_cancel)

class SeatLayoutViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    queryset = SeatLayout.objects.all()
    serializer_class = SeatLayoutSerializer
    service = SeatLayoutService()

    def create(self, request, *args, **kwargs):
        layout_name = request.data.get('layout_name')
        rows = request.data.get('rows')
        columns = request.data.get('columns')
        positions_data = request.data.get('positions', [])

        if not all([layout_name, rows, columns]):
            return Response({'detail': 'Missing required fields: layout_name, rows, columns'}, status=status.HTTP_400_BAD_REQUEST)

        def _create_seat_layout():
            seat_layout = self.service.create_seat_layout_with_positions(layout_name, rows, columns, positions_data)
            return Response(self.get_serializer(seat_layout).data, status=status.HTTP_201_CREATED)
        return self._handle_service_action(_create_seat_layout)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_seat_layout')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_seat_layout')

class SeatTypeViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer
    service = SeatTypeService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_with_service(serializer, 'create_seat_type')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.update_with_service(instance, serializer, 'update_seat_type')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_seat_type')

class SeatLayoutPositionViewSet(viewsets.ModelViewSet):
    queryset = SeatLayoutPosition.objects.all()
    serializer_class = SeatLayoutPositionSerializer
    # For simplicity, direct model interaction for SeatLayoutPosition for now.
    # Can be refactored to use a service if complex business logic is needed.

class FlightHistoryViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    queryset = FlightHistory.objects.all()
    serializer_class = FlightHistorySerializer
    service = FlightHistoryService()

    def list(self, request, *args, **kwargs):
        flight_history = self.service.flight_history_repo.get_all()
        serializer = self.get_serializer(flight_history, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_passenger(self, request):
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
        flight_id = request.query_params.get('flight_id')
        if not flight_id:
            return Response({'detail': 'Flight ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        def _by_flight():
            flight_history = self.service.get_flight_history_by_flight(flight_id)
            serializer = self.get_serializer(flight_history, many=True)
            return Response(serializer.data)
        return self._handle_service_action(_by_flight)

class TicketViewSet(ServiceActionMixin, viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    service = TicketService()

    def list(self, request, *args, **kwargs):
        tickets = self.service.ticket_repo.get_all()
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.destroy_with_service(instance, 'delete_ticket')

    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None): # pk here is reservation_id
        def _issue():
            ticket = self.service.issue_ticket(pk)
            return Response(self.get_serializer(ticket).data, status=status.HTTP_201_CREATED)
        return self._handle_service_action(_issue)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None): # pk here is ticket_id
        def _cancel():
            ticket = self.service.cancel_ticket(pk)
            return Response(self.get_serializer(ticket).data)
        return self._handle_service_action(_cancel)
