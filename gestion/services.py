from .repositories import FlightRepository, PassengerRepository, SeatRepository, BookingRepository
from django.contrib.auth.models import User
import secrets
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string

class FlightService:
    def __init__(self):
        self.flight_repository = FlightRepository()
        self.seat_repository = SeatRepository()
        self.booking_repository = BookingRepository()

    def get_all_flights(self):
        return self.flight_repository.get_all()

    def get_flight_details(self, flight_id):
        flight = self.flight_repository.get_by_id(flight_id)
        seats = self.seat_repository.get_by_flight(flight)
        return flight, seats

    def get_passenger_report(self, flight_id):
        flight = self.flight_repository.get_by_id(flight_id)
        bookings = self.booking_repository.get_by_flight(flight)
        return flight, bookings

class PassengerService:
    def __init__(self):
        self.passenger_repository = PassengerRepository()

    def create_passenger(self, first_name, last_name, document_id, email, phone):
        # Create a new user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
        )
        return self.passenger_repository.create(user, first_name, last_name, document_id, email, phone)

class BookingService:
    def __init__(self):
        self.seat_repository = SeatRepository()
        self.booking_repository = BookingRepository()
        self.passenger_repository = PassengerRepository()

    def book_seat(self, seat_id, user):
        seat = self.seat_repository.get_by_id(seat_id)
        if seat.status != 'available':
            raise Exception("This seat is not available.")
        
        passenger = self.passenger_repository.get_by_user(user)
        
        if self.booking_repository.get_by_flight(seat.flight).filter(passenger=passenger).exists():
            raise Exception("You already have a booking on this flight.")
            
        seat.status = 'reserved'
        self.seat_repository.save(seat)
        
        booking = self.booking_repository.create(seat.flight, passenger, seat)
        
        # Send email
        html_message = render_to_string('gestion/ticket_email.html', {'booking': booking})
        send_mail(
            'Booking Confirmation',
            '',
            'no-reply@airline.com',
            [passenger.email],
            fail_silently=False,
            html_message=html_message
        )
        
        return booking

    def get_ticket(self, booking_id):
        return self.booking_repository.get_by_id(booking_id)
