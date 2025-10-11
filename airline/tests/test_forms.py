from django.test import TestCase
from django.contrib.auth.models import User
from airline.forms import CustomUserCreationForm, ReservationForm, TicketForm
from airline.models import Flight, Passenger, Seat, Reservation, Airplane
from django.utils import timezone
from datetime import timedelta

class CustomUserCreationFormTest(TestCase):
    def test_valid_form(self):
        form = CustomUserCreationForm(data={
            'username': 'testuserform',
            'email': 'testform@example.com',
            'password1': 'VeryStrongPassword123!@#',
            'password2': 'VeryStrongPassword123!@#',
        })
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_invalid_form_no_email(self):
        form = CustomUserCreationForm(data={
            'username': 'testuserform',
            'password1': 'VeryStrongPassword123!@#',
            'password2': 'VeryStrongPassword123!@#',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_form_duplicate_email(self):
        User.objects.create_user(username='existinguser', email='duplicate@example.com', password='VeryStrongPassword123!@#')
        form = CustomUserCreationForm(data={
            'username': 'newuserform',
            'email': 'duplicate@example.com',
            'password1': 'VeryStrongPassword123!@#',
            'password2': 'VeryStrongPassword123!@#',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class ReservationFormTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            origin="EZE",
            destination="MIA",
            departure_date=timezone.now() + timedelta(days=1),
            arrival_date=timezone.now() + timedelta(days=1, hours=3),
            duration=timedelta(hours=3),
            status="Scheduled",
            base_price=500.00
        )
        self.passenger = Passenger.objects.create(
            first_name="John",
            last_name="Doe",
            document_number="123456789",
            email="john.doe@example.com",
            date_of_birth="1990-01-01",
            document_type="DNI"
        )
        self.seat = Seat.objects.create(
            airplane=self.airplane,
            number="1A",
            row=1,
            column="A",
            type="ECO",
            status="Available"
        )

    def test_valid_reservation_form(self):
        form = ReservationForm(
            initial={'flight': self.flight}, # Pass flight in initial to filter seats correctly
            data={
                'flight': self.flight.id,
                'seat': self.seat.id,
                'status': 'PEN',
                'price': 500.00
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_reservation_form_initial_queryset(self):
        form = ReservationForm(initial={'flight': self.flight})
        self.assertQuerySetEqual(form.fields['seat'].queryset, Seat.objects.filter(airplane=self.airplane, status='Available'), transform=lambda x: x)

class TicketFormTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            origin="EZE",
            destination="MIA",
            departure_date=timezone.now() + timedelta(days=1),
            arrival_date=timezone.now() + timedelta(days=1, hours=3),
            duration=timedelta(hours=3),
            status="Scheduled",
            base_price=500.00
        )
        self.passenger = Passenger.objects.create(
            first_name="John",
            last_name="Doe",
            document_number="123456789",
            email="john.doe@example.com",
            date_of_birth="1990-01-01",
            document_type="DNI"
        )
        self.seat = Seat.objects.create(
            airplane=self.airplane,
            number="1A",
            row=1,
            column="A",
            type="ECO",
            status="Reserved"
        )
        self.reservation = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            status="CON",
            price=500.00,
            reservation_code="RES12345"
        )

    def test_valid_ticket_form(self):
        form = TicketForm(data={
            'reservation': self.reservation.id,
            'barcode': 'BARCODE12345',
            'status': 'EMI'
        })
        self.assertTrue(form.is_valid())

    def test_ticket_form_barcode_generation(self):
        form = TicketForm()
        self.assertIsNotNone(form.initial['barcode'])
        self.assertEqual(len(form.initial['barcode']), 20)

    def test_ticket_form_reservation_queryset(self):
        form = TicketForm()
        self.assertQuerySetEqual(form.fields['reservation'].queryset, Reservation.objects.filter(status='CON'), transform=lambda x: x)
