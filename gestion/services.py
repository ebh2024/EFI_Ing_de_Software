from .repositories import FlightRepository, PassengerRepository, SeatRepository, BookingRepository, NotificationRepository
from django.contrib.auth.models import User
import secrets
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Flight

class FlightService:
    def __init__(self):
        self.flight_repository = FlightRepository()
        self.seat_repository = SeatRepository()
        self.booking_repository = BookingRepository()

    def get_all_flights(self):
        return self.flight_repository.get_all()

    def search_flights(self, origin, destination, departure_date):
        flights = self.flight_repository.get_all()
        if origin:
            flights = flights.filter(origin__icontains=origin)
        if destination:
            flights = flights.filter(destination__icontains=destination)
        if departure_date:
            flights = flights.filter(departure_date__date=departure_date)
        return flights

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

    def get_passenger_by_user(self, user):
        passenger, created = self.passenger_repository.get_or_create_by_user(user)
        return passenger

    def update_passenger(self, passenger, data):
        passenger.first_name = data['first_name']
        passenger.last_name = data['last_name']
        passenger.document_id = data['document_id']
        passenger.email = data['email']
        passenger.phone = data['phone']
        passenger.save()
        # Update the associated User model's email as well
        passenger.user.email = data['email']
        passenger.user.username = data['email'] # Assuming username is also email
        passenger.user.save()
        return passenger

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

    def get_bookings_by_passenger(self, passenger):
        return self.booking_repository.get_by_passenger(passenger)

class NotificationService:
    def __init__(self):
        self.notification_repository = NotificationRepository()

    def create_notification(self, recipient, message, flight=None):
        return self.notification_repository.create(recipient, message, flight)

    def get_unread_notifications(self, user):
        return self.notification_repository.get_unread_notifications(user)

    def mark_notification_as_read(self, notification):
        self.notification_repository.mark_as_read(notification)

@receiver(post_save, sender=Flight)
def flight_update_notification(sender, instance, created, **kwargs):
    if not created: # Only send notifications for updates, not new flights
        # This is a simplified example. In a real app, you'd compare old vs. new instance
        # to determine what changed (e.g., departure_date, status).
        # For now, let's assume any save means a potential change.
        
        # Get all passengers booked on this flight
        bookings = instance.booking_set.all()
        notification_service = NotificationService()
        
        for booking in bookings:
            message = f"Update for your flight {instance.origin} to {instance.destination} on {instance.departure_date.strftime('%d/%m/%Y %H:%M')}. Please check flight details."
            notification_service.create_notification(booking.passenger.user, message, instance)
