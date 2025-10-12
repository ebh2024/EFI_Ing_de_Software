from rest_framework import viewsets
from .models import Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket
from .serializers import AirplaneSerializer, FlightSerializer, PassengerSerializer, ReservationSerializer, SeatLayoutSerializer, SeatTypeSerializer, SeatLayoutPositionSerializer, FlightHistorySerializer, TicketSerializer

class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class SeatLayoutViewSet(viewsets.ModelViewSet):
    queryset = SeatLayout.objects.all()
    serializer_class = SeatLayoutSerializer

class SeatTypeViewSet(viewsets.ModelViewSet):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer

class SeatLayoutPositionViewSet(viewsets.ModelViewSet):
    queryset = SeatLayoutPosition.objects.all()
    serializer_class = SeatLayoutPositionSerializer

class FlightHistoryViewSet(viewsets.ModelViewSet):
    queryset = FlightHistory.objects.all()
    serializer_class = FlightHistorySerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
