from rest_framework import serializers
from .models import Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket, Seat

class SeatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatType
        fields = '__all__'

class SeatLayoutPositionSerializer(serializers.ModelSerializer):
    seat_type = serializers.PrimaryKeyRelatedField(queryset=SeatType.objects.all())
    seat_number = serializers.CharField(read_only=True)

    class Meta:
        model = SeatLayoutPosition
        fields = '__all__'

class SeatLayoutSerializer(serializers.ModelSerializer):
    positions = SeatLayoutPositionSerializer(many=True, read_only=True)

    class Meta:
        model = SeatLayout
        fields = '__all__'

class AirplaneSerializer(serializers.ModelSerializer):
    seat_layout = serializers.PrimaryKeyRelatedField(queryset=SeatLayout.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Airplane
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())

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
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    passenger = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())

    class Meta:
        model = Reservation
        fields = '__all__'

class FlightHistorySerializer(serializers.ModelSerializer):
    passenger = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())

    class Meta:
        model = FlightHistory
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    reservation = serializers.PrimaryKeyRelatedField(queryset=Reservation.objects.all())
    ticket_number = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
