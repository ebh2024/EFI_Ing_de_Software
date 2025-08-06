from .models import Flight, Seat, Passenger, Booking, Notification
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid # For generating unique transaction IDs

class FlightService:
    def search_flights(self, origin, destination, departure_date):
        flights = Flight.objects.all()
        if origin:
            flights = flights.filter(origin__icontains=origin)
        if destination:
            flights = flights.filter(destination__icontains=destination)
        if departure_date:
            flights = flights.filter(departure_date__date=departure_date)
        return flights

    def get_flight_details(self, flight_id):
        flight = get_object_or_404(Flight, id=flight_id)
        seats = Seat.objects.filter(flight=flight).order_by('number')
        return flight, seats

    def get_passenger_report(self, flight_id):
        flight = get_object_or_404(Flight, id=flight_id)
        bookings = Booking.objects.filter(flight=flight, payment_status='completed').select_related('passenger', 'seat')
        return flight, bookings

class PassengerService:
    def create_passenger(self, first_name, last_name, document_id, email, phone):
        # Assuming user is already created or will be created separately
        # For simplicity, let's assume a user is passed or created here
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        if created:
            user.set_unusable_password() # User will set password later or use social login
            user.save()

        passenger = Passenger.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            document_id=document_id,
            email=email,
            phone=phone
        )
        return passenger

    def get_passenger_by_user(self, user):
        return get_object_or_404(Passenger, user=user)

    def update_passenger(self, passenger, data):
        passenger.first_name = data.get('first_name', passenger.first_name)
        passenger.last_name = data.get('last_name', passenger.last_name)
        passenger.document_id = data.get('document_id', passenger.document_id)
        passenger.email = data.get('email', passenger.email)
        passenger.phone = data.get('phone', passenger.phone)
        passenger.save()
        return passenger

class BookingService:
    def book_seat(self, seat_id, user):
        with transaction.atomic():
            seat = get_object_or_404(Seat, id=seat_id)
            if seat.status != 'available':
                raise ValidationError("Seat is not available.")

            passenger = get_object_or_404(Passenger, user=user)

            # Check if the passenger already has a booking for this flight
            if Booking.objects.filter(flight=seat.flight, passenger=passenger, payment_status='completed').exists():
                raise ValidationError("You already have a completed booking for this flight.")

            # Create a pending booking
            booking = Booking.objects.create(
                flight=seat.flight,
                passenger=passenger,
                seat=seat,
                payment_status='pending' # Initial status is pending payment
            )
            seat.status = 'reserved'
            seat.save()
            return booking

    def get_ticket(self, booking_id):
        return get_object_or_404(Booking, id=booking_id)

    def get_bookings_by_passenger(self, passenger):
        return Booking.objects.filter(passenger=passenger).order_by('-booking_date')

    def process_payment(self, booking_id):
        with transaction.atomic():
            booking = get_object_or_404(Booking, id=booking_id)

            if booking.payment_status == 'completed':
                raise ValidationError("Payment for this booking has already been completed.")

            # Simulate payment processing
            # In a real application, this would involve calling a payment gateway API
            # and handling success/failure responses.
            payment_successful = True # Simulate a successful payment

            if payment_successful:
                booking.payment_status = 'completed'
                booking.transaction_id = str(uuid.uuid4()) # Generate a unique transaction ID
                booking.payment_date = timezone.now()
                booking.save()

                # Update seat status to occupied after successful payment
                if booking.seat:
                    booking.seat.status = 'occupied'
                    booking.seat.save()

                # Optionally send a notification
                NotificationService().create_notification(
                    booking.passenger.user,
                    f"Your payment for flight {booking.flight.origin} to {booking.flight.destination} has been successfully processed. Booking ID: {booking.id}",
                    booking.flight
                )
                return booking
            else:
                booking.payment_status = 'failed'
                booking.save()
                raise ValidationError("Payment failed. Please try again.")

class NotificationService:
    def create_notification(self, recipient, message, flight=None):
        Notification.objects.create(recipient=recipient, message=message, flight=flight)

    def get_unread_notifications(self, user):
        return Notification.objects.filter(recipient=user, is_read=False).order_by('-created_at')

    def mark_notification_as_read(self, notification):
        notification.is_read = True
        notification.save()
