from rest_framework import serializers
from .models import Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket, Seat

class SeatTypeSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo SeatType.

    Convierte instancias de SeatType a JSON y viceversa.
    """
    class Meta:
        model = SeatType
        fields = '__all__'

class SeatLayoutPositionSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo SeatLayoutPosition.

    Incluye campos relacionados y calculados como seat_number.
    """
    seat_type = serializers.PrimaryKeyRelatedField(queryset=SeatType.objects.all())
    seat_number = serializers.CharField(read_only=True)

    class Meta:
        model = SeatLayoutPosition
        fields = '__all__'

class SeatLayoutSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo SeatLayout.

    Incluye posiciones relacionadas de forma anidada.
    """
    positions = SeatLayoutPositionSerializer(many=True, read_only=True)

    class Meta:
        model = SeatLayout
        fields = '__all__'

class AirplaneSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Airplane.

    Maneja relación con SeatLayout opcional.
    """
    seat_layout = serializers.PrimaryKeyRelatedField(queryset=SeatLayout.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Airplane
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Flight.

    Requiere relación con Airplane.
    """
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())

    class Meta:
        model = Flight
        fields = '__all__'

class PassengerSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Passenger.

    Convierte instancias de Passenger a JSON y viceversa.
    """
    class Meta:
        model = Passenger
        fields = '__all__'

class SeatSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Seat.

    Maneja relación opcional con SeatType.
    """
    seat_type = serializers.PrimaryKeyRelatedField(queryset=SeatType.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Seat
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Reservation.

    Requiere relaciones con Flight, Passenger y Seat.
    """
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    passenger = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())

    class Meta:
        model = Reservation
        fields = '__all__'

class FlightHistorySerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo FlightHistory.

    Requiere relaciones con Passenger y Flight.
    """
    passenger = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())

    class Meta:
        model = FlightHistory
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Ticket.

    Incluye campo calculado ticket_number y relación con Reservation.
    """
    reservation = serializers.PrimaryKeyRelatedField(queryset=Reservation.objects.all())
    ticket_number = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
