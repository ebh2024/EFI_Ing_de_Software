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

class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    service = AirplaneService() # Keep service for custom actions if needed

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            airplane = self.service.create_airplane_with_seats(serializer.validated_data)
            headers = self.get_success_headers(serializer.data)
            return Response(self.get_serializer(airplane).data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            airplane = self.service.update_airplane(instance.pk, serializer.validated_data)
            return Response(self.get_serializer(airplane).data)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.service.delete_airplane(instance.pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    service = FlightService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            flight = self.service.create_flight(serializer.validated_data)
            headers = self.get_success_headers(serializer.data)
            return Response(self.get_serializer(flight).data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            flight = self.service.update_flight(instance.pk, serializer.validated_data)
            return Response(self.get_serializer(flight).data)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.service.delete_flight(instance.pk):
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

class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    service = PassengerService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            passenger = self.service.create_passenger(serializer.validated_data)
            headers = self.get_success_headers(serializer.data)
            return Response(self.get_serializer(passenger).data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            passenger = self.service.update_passenger(instance.pk, serializer.validated_data)
            return Response(self.get_serializer(passenger).data)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.service.delete_passenger(instance.pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    service = ReservationService()

    def create(self, request, *args, **kwargs):
        # This create method is custom to handle the service logic
        flight_id = request.data.get('flight')
        passenger_id = request.data.get('passenger')
        seat_id = request.data.get('seat')
        price = request.data.get('price')

        if not all([flight_id, passenger_id, seat_id, price]):
            return Response({'detail': 'Missing required fields: flight, passenger, seat, price'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = self.service.create_reservation(flight_id, passenger_id, seat_id, price)
            return Response(self.get_serializer(reservation).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            reservation = self.service.update_reservation(instance.pk, serializer.validated_data)
            return Response(self.get_serializer(reservation).data)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.service.delete_reservation(instance.pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        try:
            reservation = self.service.confirm_reservation(pk)
            return Response(self.get_serializer(reservation).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            reservation = self.service.cancel_reservation(pk)
            return Response(self.get_serializer(reservation).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SeatLayoutViewSet(viewsets.ModelViewSet):
    queryset = SeatLayout.objects.all()
    serializer_class = SeatLayoutSerializer
    service = SeatLayoutService()

    def create(self, request, *args, **kwargs):
        # Custom create for seat layout with positions
        layout_name = request.data.get('layout_name')
        rows = request.data.get('rows')
        columns = request.data.get('columns')
        positions_data = request.data.get('positions', [])

        if not all([layout_name, rows, columns]):
            return Response({'detail': 'Missing required fields: layout_name, rows, columns'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            seat_layout = self.service.create_seat_layout_with_positions(layout_name, rows, columns, positions_data)
            return Response(self.get_serializer(seat_layout).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            seat_layout = self.service.update_seat_layout(instance.pk, serializer.validated_data)
            return Response(self.get_serializer(seat_layout).data)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.service.delete_seat_layout(instance.pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class SeatTypeViewSet(viewsets.ModelViewSet):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer
    service = SeatTypeService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            seat_type = self.service.create_seat_type(serializer.validated_data)
            headers = self.get_success_headers(serializer.data)
            return Response(self.get_serializer(seat_type).data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            seat_type = self.service.update_seat_type(instance.pk, serializer.validated_data)
            return Response(self.get_serializer(seat_type).data)
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.service.delete_seat_type(instance.pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class SeatLayoutPositionViewSet(viewsets.ModelViewSet):
    queryset = SeatLayoutPosition.objects.all()
    serializer_class = SeatLayoutPositionSerializer
    # For simplicity, direct model interaction for SeatLayoutPosition for now.
    # Can be refactored to use a service if complex business logic is needed.

class FlightHistoryViewSet(viewsets.ModelViewSet):
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

    # No create, update, delete for FlightHistory as it's typically generated by other actions (e.g., reservation)

    @action(detail=False, methods=['get'])
    def by_passenger(self, request):
        passenger_id = request.query_params.get('passenger_id')
        if not passenger_id:
            return Response({'detail': 'Passenger ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            flight_history = self.service.get_flight_history_by_passenger(passenger_id)
            serializer = self.get_serializer(flight_history, many=True)
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
            serializer = self.get_serializer(flight_history, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TicketViewSet(viewsets.ModelViewSet):
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
        if not self.service.delete_ticket(instance.pk):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None): # pk here is reservation_id
        try:
            ticket = self.service.issue_ticket(pk)
            return Response(self.get_serializer(ticket).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None): # pk here is ticket_id
        try:
            ticket = self.service.cancel_ticket(pk)
            return Response(self.get_serializer(ticket).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
