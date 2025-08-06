from .models import Flight, Passenger, Aircraft, Booking, Seat, Notification

class FlightRepository:
    def get_all(self):
        return Flight.objects.all()

    def get_by_id(self, flight_id):
        return Flight.objects.get(pk=flight_id)

class PassengerRepository:
    def get_by_user(self, user):
        return Passenger.objects.get(user=user)

    def get_or_create_by_user(self, user):
        return Passenger.objects.get_or_create(user=user, defaults={'first_name': '', 'last_name': '', 'document_id': '', 'email': user.email, 'phone': ''})

    def create(self, user, first_name, last_name, document_id, email, phone):
        return Passenger.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            document_id=document_id,
            email=email,
            phone=phone
        )
    
    def save(self, passenger):
        passenger.save()

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

    def get_by_passenger(self, passenger):
        return Booking.objects.filter(passenger=passenger)

class NotificationRepository:
    def create(self, recipient, message, flight=None):
        return Notification.objects.create(recipient=recipient, message=message, flight=flight)

    def get_unread_notifications(self, user):
        return Notification.objects.filter(recipient=user, is_read=False).order_by('-created_at')

    def mark_as_read(self, notification):
        notification.is_read = True
        notification.save()
