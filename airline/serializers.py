from rest_framework import serializers
from .models import Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket, Seat

class SeatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatType
        fields = '__all__'

class SeatLayoutPositionSerializer(serializers.ModelSerializer):
    seat_type = SeatTypeSerializer(read_only=True)

    class Meta:
        model = SeatLayoutPosition
        fields = '__all__'

class SeatLayoutSerializer(serializers.ModelSerializer):
    positions = SeatLayoutPositionSerializer(many=True, read_only=True)

    class Meta:
        model = SeatLayout
        fields = '__all__'

class AirplaneSerializer(serializers.ModelSerializer):
    seat_layout = SeatLayoutSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    airplane = AirplaneSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = '__all__'

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = '__all__'

class SeatSerializer(serializers.ModelSerializer):
    seat_type = SeatTypeSerializer(read_only=True)

    class Meta:
        model = Seat
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)
    passenger = PassengerSerializer(read_only=True)
    seat = SeatSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'

class FlightHistorySerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(read_only=True)
    flight = FlightSerializer(read_only=True)

    class Meta:
        model = FlightHistory
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
