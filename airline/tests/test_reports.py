from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from airline.models import (
    Airplane, Flight, Passenger, Reservation, FlightHistory,
    SeatLayout, SeatType, SeatLayoutPosition, Seat
)
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

User = get_user_model()

class ReportViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Create SeatType
        self.economy_seat_type = SeatType.objects.create(name='Economy', code='ECO', price_multiplier=Decimal('1.00'))
        self.premium_seat_type = SeatType.objects.create(name='Premium', code='PRE', price_multiplier=Decimal('1.50'))

        # Create SeatLayout
        self.seat_layout = SeatLayout.objects.create(layout_name='TestLayout', rows=10, columns=6)
        SeatLayoutPosition.objects.create(seat_layout=self.seat_layout, seat_type=self.economy_seat_type, row=1, column='A')
        SeatLayoutPosition.objects.create(seat_layout=self.seat_layout, seat_type=self.premium_seat_type, row=1, column='B')

        # Create Airplane
        self.airplane = Airplane.objects.create(
            model_name='Boeing 747',
            registration_number='TEST001',
            capacity=100,
            seat_layout=self.seat_layout
        )

        # Create Seats for the airplane based on the layout
        for r in range(1, self.seat_layout.rows + 1):
            for c_idx in range(self.seat_layout.columns):
                column_char = chr(ord('A') + c_idx)
                seat_type = self.economy_seat_type # Default
                if r == 1 and column_char == 'B':
                    seat_type = self.premium_seat_type
                Seat.objects.create(
                    airplane=self.airplane,
                    number=f"{r}{column_char}",
                    row=r,
                    column=column_char,
                    seat_type=seat_type,
                    status='Available'
                )

        # Create Flight
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            origin='JFK',
            destination='LAX',
            departure_date=datetime.now() + timedelta(days=1),
            arrival_date=datetime.now() + timedelta(days=1, hours=5),
            duration=timedelta(hours=5),
            status='Scheduled',
            base_price=Decimal('200.00')
        )

        # Create Passenger
        self.passenger1 = Passenger.objects.create(
            first_name='John',
            last_name='Doe',
            document_number='123456789',
            email='john.doe@example.com',
            phone='1234567890',
            date_of_birth='1990-01-01'
        )
        self.passenger2 = Passenger.objects.create(
            first_name='Jane',
            last_name='Smith',
            document_number='987654321',
            email='jane.smith@example.com',
            phone='0987654321',
            date_of_birth='1992-02-02'
        )
        
        # Create seats for reservation
        self.seat1A = Seat.objects.get(airplane=self.airplane, row=1, column='A')
        self.seat1B = Seat.objects.get(airplane=self.airplane, row=1, column='B')

        # Create Reservation 1
        self.reservation1 = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger1,
            seat=self.seat1A,
            status='CON',
            price=self.flight.base_price * self.economy_seat_type.price_multiplier,
            reservation_code=str(uuid.uuid4()).replace('-', '')[:20]
        )

        # Create FlightHistory entry 1
        FlightHistory.objects.create(
            passenger=self.passenger1,
            flight=self.flight,
            seat_number=self.seat1A.number,
            price_paid=self.reservation1.price
        )

        # Create Reservation 2
        self.reservation2 = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger2,
            seat=self.seat1B,
            status='CON',
            price=self.flight.base_price * self.premium_seat_type.price_multiplier,
            reservation_code=str(uuid.uuid4()).replace('-', '')[:20]
        )

        # Create FlightHistory entry 2
        FlightHistory.objects.create(
            passenger=self.passenger2,
            flight=self.flight,
            seat_number=self.seat1B.number,
            price_paid=self.reservation2.price
        )

    def test_reservation_list_view(self):
        response = self.client.get(reverse('reservation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/reservation_list.html')
        self.assertIn('reservations', response.context)
        self.assertEqual(len(response.context['reservations']), 2) # Now two reservations
        self.assertContains(response, self.reservation1.reservation_code)
        self.assertContains(response, self.passenger1.first_name)
        self.assertContains(response, self.flight.origin)
        self.assertContains(response, self.flight.destination)
        self.assertContains(response, self.reservation2.reservation_code)
        self.assertContains(response, self.passenger2.first_name)

    def test_passenger_flight_history_view(self):
        response = self.client.get(reverse('passenger_flight_history', args=[self.passenger1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/passenger_flight_history.html')
        self.assertIn('passenger', response.context)
        self.assertEqual(response.context['passenger'], self.passenger1)
        self.assertIn('flight_history', response.context)
        self.assertEqual(len(response.context['flight_history']), 1)
        self.assertContains(response, self.passenger1.first_name)
        self.assertContains(response, self.flight.origin)
        self.assertContains(response, self.flight.destination)
        self.assertContains(response, '200.00')

    def test_passenger_list_by_flight_view(self):
        response = self.client.get(reverse('passenger_list_by_flight', args=[self.flight.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/passenger_list_by_flight.html')
        self.assertIn('flight', response.context)
        self.assertEqual(response.context['flight'], self.flight)
        self.assertIn('passengers', response.context)
        self.assertEqual(len(response.context['passengers']), 2) # Two passengers on this flight
        self.assertContains(response, self.passenger1.first_name)
        self.assertContains(response, self.passenger2.first_name)
        self.assertContains(response, self.seat1A.number)
        self.assertContains(response, self.seat1B.number)
