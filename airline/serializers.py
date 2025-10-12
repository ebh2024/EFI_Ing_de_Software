from rest_framework import serializers
from .models import Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket

class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class SeatLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatLayout
        fields = '__all__'

class SeatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatType
        fields = '__all__'

class SeatLayoutPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatLayoutPosition
        fields = '__all__'

class FlightHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightHistory
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
