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

class AirplaneViewSet(viewsets.ViewSet):
    service = AirplaneService()
    serializer_class = AirplaneSerializer

    def list(self, request):
        airplanes = self.service.airplane_repo.get_all()
        serializer = self.serializer_class(airplanes, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        airplane = self.service.get_airplane(pk)
        if not airplane:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(airplane)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                airplane = self.service.create_airplane_with_seats(serializer.validated_data)
                return Response(self.serializer_class(airplane).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                airplane = self.service.update_airplane(pk, serializer.validated_data)
                if not airplane:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(self.serializer_class(airplane).data)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        if not self.service.delete_airplane(pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FlightViewSet(viewsets.ViewSet):
    service = FlightService()
    serializer_class = FlightSerializer

    def list(self, request):
        flights = self.service.flight_repo.get_all()
        serializer = self.serializer_class(flights, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        flight = self.service.get_flight(pk)
        if not flight:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(flight)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                flight = self.service.create_flight(serializer.validated_data)
                return Response(self.serializer_class(flight).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                flight = self.service.update_flight(pk, serializer.validated_data)
                if not flight:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(self.serializer_class(flight).data)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        if not self.service.delete_flight(pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

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

class PassengerViewSet(viewsets.ViewSet):
    service = PassengerService()
    serializer_class = PassengerSerializer

    def list(self, request):
        passengers = self.service.passenger_repo.get_all()
        serializer = self.serializer_class(passengers, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        passenger = self.service.get_passenger(pk)
        if not passenger:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(passenger)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                passenger = self.service.create_passenger(serializer.validated_data)
                return Response(self.serializer_class(passenger).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                passenger = self.service.update_passenger(pk, serializer.validated_data)
                if not passenger:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(self.serializer_class(passenger).data)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        if not self.service.delete_passenger(pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReservationViewSet(viewsets.ViewSet):
    service = ReservationService()
    serializer_class = ReservationSerializer

    def list(self, request):
        reservations = self.service.reservation_repo.get_all()
        serializer = self.serializer_class(reservations, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        reservation = self.service.get_reservation(pk)
        if not reservation:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(reservation)
        return Response(serializer.data)

    def create(self, request):
        # This create method is custom to handle the service logic
        flight_id = request.data.get('flight')
        passenger_id = request.data.get('passenger')
        seat_id = request.data.get('seat')
        price = request.data.get('price')

        if not all([flight_id, passenger_id, seat_id, price]):
            return Response({'detail': 'Missing required fields: flight, passenger, seat, price'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = self.service.create_reservation(flight_id, passenger_id, seat_id, price)
            return Response(self.serializer_class(reservation).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        try:
            reservation = self.service.confirm_reservation(pk)
            return Response(self.serializer_class(reservation).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            reservation = self.service.cancel_reservation(pk)
            return Response(self.serializer_class(reservation).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SeatLayoutViewSet(viewsets.ViewSet):
    service = SeatLayoutService()
    serializer_class = SeatLayoutSerializer

    def list(self, request):
        seat_layouts = self.service.seat_layout_repo.get_all()
        serializer = self.serializer_class(seat_layouts, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        seat_layout = self.service.get_seat_layout(pk)
        if not seat_layout:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(seat_layout)
        return Response(serializer.data)

    def create(self, request):
        # Custom create for seat layout with positions
        layout_name = request.data.get('layout_name')
        rows = request.data.get('rows')
        columns = request.data.get('columns')
        positions_data = request.data.get('positions', [])

        if not all([layout_name, rows, columns]):
            return Response({'detail': 'Missing required fields: layout_name, rows, columns'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            seat_layout = self.service.create_seat_layout_with_positions(layout_name, rows, columns, positions_data)
            return Response(self.serializer_class(seat_layout).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                seat_layout = self.service.update_seat_layout(pk, serializer.validated_data)
                if not seat_layout:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(self.serializer_class(seat_layout).data)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        if not self.service.delete_seat_layout(pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class SeatTypeViewSet(viewsets.ViewSet):
    service = SeatTypeService()
    serializer_class = SeatTypeSerializer

    def list(self, request):
        seat_types = self.service.seat_type_repo.get_all()
        serializer = self.serializer_class(seat_types, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        seat_type = self.service.get_seat_type(pk)
        if not seat_type:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(seat_type)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                seat_type = self.service.create_seat_type(serializer.validated_data)
                return Response(self.serializer_class(seat_type).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                seat_type = self.service.update_seat_type(pk, serializer.validated_data)
                if not seat_type:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(self.serializer_class(seat_type).data)
            except ValidationError as e:
                return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_BAD_REQUEST)

    def destroy(self, request, pk=None):
        if not self.service.delete_seat_type(pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class SeatLayoutPositionViewSet(viewsets.ModelViewSet):
    queryset = SeatLayoutPosition.objects.all()
    serializer_class = SeatLayoutPositionSerializer
    # For simplicity, direct model interaction for SeatLayoutPosition for now.
    # Can be refactored to use a service if complex business logic is needed.

class FlightHistoryViewSet(viewsets.ViewSet):
    service = FlightHistoryService()
    serializer_class = FlightHistorySerializer

    def list(self, request):
        flight_history = self.service.flight_history_repo.get_all()
        serializer = self.serializer_class(flight_history, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        flight_history_entry = self.service.flight_history_repo.get_by_id(pk)
        if not flight_history_entry:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(flight_history_entry)
        return Response(serializer.data)

    # No create, update, delete for FlightHistory as it's typically generated by other actions (e.g., reservation)

    @action(detail=False, methods=['get'])
    def by_passenger(self, request):
        passenger_id = request.query_params.get('passenger_id')
        if not passenger_id:
            return Response({'detail': 'Passenger ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            flight_history = self.service.get_flight_history_by_passenger(passenger_id)
            serializer = self.serializer_class(flight_history, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def by_flight(self, request):
        flight_id = request.query_params.get('flight_id')
        if not flight_id:
            return Response({'detail': 'Flight ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            flight_history = self.service.get_flight_history_by_flight(flight_id)
            serializer = self.serializer_class(flight_history, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TicketViewSet(viewsets.ViewSet):
    service = TicketService()
    serializer_class = TicketSerializer

    def list(self, request):
        tickets = self.service.ticket_repo.get_all()
        serializer = self.serializer_class(tickets, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        ticket = self.service.get_ticket(pk)
        if not ticket:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None): # pk here is reservation_id
        try:
            ticket = self.service.issue_ticket(pk)
            return Response(self.serializer_class(ticket).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None): # pk here is ticket_id
        try:
            ticket = self.service.cancel_ticket(pk)
            return Response(self.serializer_class(ticket).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
