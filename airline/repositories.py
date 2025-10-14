from django.shortcuts import get_object_or_404
from .models import Airplane, Flight, Passenger, Reservation, Seat, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket

class BaseRepository:
    model = None

    def get_by_id(self, pk):
        return get_object_or_404(self.model, pk=pk)

    def get_all(self):
        return self.model.objects.all()

    def create(self, data):
        return self.model.objects.create(**data)

    def update(self, pk, data):
        obj = self.get_by_id(pk)
        for attr, value in data.items():
            setattr(obj, attr, value)
        obj.save()
        return obj

    def delete(self, pk):
        obj = self.get_by_id(pk)
        obj.delete()
        return True

class AirplaneRepository(BaseRepository):
    model = Airplane

class FlightRepository(BaseRepository):
    model = Flight

class PassengerRepository(BaseRepository):
    model = Passenger

    def get_or_create_passenger(self, email, defaults):
        return self.model.objects.get_or_create(email=email, defaults=defaults)

class ReservationRepository(BaseRepository):
    model = Reservation

    def filter_by_flight_seat_status(self, flight, seat, statuses):
        return self.model.objects.filter(flight=flight, seat=seat, status__in=statuses)

    def filter_by_flight_and_select_related(self, flight):
        return self.model.objects.filter(flight=flight).select_related('passenger', 'seat')

class SeatRepository(BaseRepository):
    model = Seat

    def filter_by_airplane_ordered(self, airplane):
        return self.model.objects.filter(airplane=airplane).order_by('row', 'column')

class SeatLayoutRepository(BaseRepository):
    model = SeatLayout

class SeatTypeRepository(BaseRepository):
    model = SeatType

class SeatLayoutPositionRepository(BaseRepository):
    model = SeatLayoutPosition

class FlightHistoryRepository(BaseRepository):
    model = FlightHistory

    def filter_by_passenger_ordered(self, passenger):
        return self.model.objects.filter(passenger=passenger).order_by('-booking_date')

    def filter_by_flight(self, flight_id):
        return self.model.objects.filter(flight__id=flight_id)

    def filter_by_passenger(self, passenger_id):
        return self.model.objects.filter(passenger__id=passenger_id)

class TicketRepository(BaseRepository):
    model = Ticket

    def get_or_create_ticket(self, reservation, defaults):
        return self.model.objects.get_or_create(reservation=reservation, defaults=defaults)
