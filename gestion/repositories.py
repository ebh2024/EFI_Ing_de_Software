from .models import Flight, Passenger, Aircraft, Booking, Seat

class FlightRepository:
    def get_all(self):
        return Flight.objects.all()

    def get_by_id(self, flight_id):
        return Flight.objects.get(pk=flight_id)

class PassengerRepository:
    def get_by_user(self, user):
        return Passenger.objects.get(user=user)

    def create(self, user, first_name, last_name, document_id, email, phone):
        return Passenger.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            document_id=document_id,
            email=email,
            phone=phone
        )

class SeatRepository:
    def get_by_id(self, seat_id):
        return Seat.objects.get(pk=seat_id)

    def get_by_flight(self, flight):
        return Seat.objects.filter(flight=flight)

    def save(self, seat):
        seat.save()

class BookingRepository:
    def create(self, flight, passenger, seat):
        return Booking.objects.create(
            flight=flight,
            passenger=passenger,
            seat=seat
        )

    def get_by_id(self, booking_id):
        return Booking.objects.get(pk=booking_id)

    def get_by_flight(self, flight):
        return Booking.objects.filter(flight=flight)
