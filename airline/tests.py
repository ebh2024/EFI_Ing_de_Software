from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Airplane, Flight, Passenger, Seat, Reservation, UserProfile, Ticket
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm

class AirplaneModelTest(TestCase):
    def test_create_airplane(self):
        airplane = Airplane.objects.create(model="Boeing 747", capacity=400, rows=50, columns=8)
        self.assertEqual(airplane.model, "Boeing 747")
        self.assertEqual(airplane.capacity, 400)
        self.assertEqual(str(airplane), "Boeing 747 (400 seats)")

class FlightModelTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(model="Airbus A320", capacity=150, rows=25, columns=6)
        self.departure_date = timezone.now() + timedelta(days=1)
        self.arrival_date = self.departure_date + timedelta(hours=3)

    def test_create_flight(self):
        flight = Flight.objects.create(
            airplane=self.airplane,
            origin="EZE",
            destination="MIA",
            departure_date=self.departure_date,
            arrival_date=self.arrival_date,
            duration=timedelta(hours=3),
            status="Scheduled",
            base_price=500.00
        )
        self.assertEqual(flight.origin, "EZE")
        self.assertEqual(flight.destination, "MIA")
        self.assertEqual(flight.status, "Scheduled")
        self.assertEqual(str(flight), f"Flight EZE to MIA on {self.departure_date.strftime('%Y-%m-%d %H:%M')}")

    def test_flight_clean_arrival_before_departure(self):
        flight = Flight(
            airplane=self.airplane,
            origin="EZE",
            destination="MIA",
            departure_date=self.arrival_date,
            arrival_date=self.departure_date,
            duration=timedelta(hours=3),
            status="Scheduled",
            base_price=500.00
        )
        with self.assertRaisesMessage(Exception, 'Arrival date must be after departure date.'):
            flight.full_clean()

    def test_flight_clean_departure_in_past(self):
        past_departure = timezone.now() - timedelta(days=1)
        past_arrival = past_departure + timedelta(hours=3)
        flight = Flight(
            airplane=self.airplane,
            origin="EZE",
            destination="MIA",
            departure_date=past_departure,
            arrival_date=past_arrival,
            duration=timedelta(hours=3),
            status="Scheduled",
            base_price=500.00
        )
        with self.assertRaisesMessage(Exception, 'Departure date cannot be in the past.'):
            flight.full_clean()

class PassengerModelTest(TestCase):
    def test_create_passenger(self):
        passenger = Passenger.objects.create(
            first_name="John Doe",
            document_number="12345678",
            email="john.doe@example.com",
            date_of_birth="1990-01-01",
            document_type="DNI"
        )
        self.assertEqual(passenger.first_name, "John Doe")
        self.assertEqual(passenger.email, "john.doe@example.com")
        self.assertEqual(str(passenger), "John Doe")

    def test_passenger_clean_invalid_email(self):
        passenger = Passenger(
            first_name="Jane Doe",
            document_number="87654321",
            email="jane.doeexample.com",
            date_of_birth="1995-05-05",
            document_type="PAS"
        )
        with self.assertRaisesMessage(Exception, 'Invalid email.'):
            passenger.full_clean()

class SeatModelTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)

    def test_create_seat(self):
        seat = Seat.objects.create(
            airplane=self.airplane,
            number="1A",
            row=1,
            column="A",
            type="EXE",
            status="Available"
        )
        self.assertEqual(seat.number, "1A")
        self.assertEqual(seat.type, "EXE")
        self.assertEqual(str(seat), "Seat 1A - Boeing 737")

class ReservationModelTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(model="Embraer 190", capacity=100, rows=20, columns=4)
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            origin="COR",
            destination="BUE",
            departure_date=timezone.now() + timedelta(days=2),
            arrival_date=timezone.now() + timedelta(days=2, hours=1),
            duration=timedelta(hours=1),
            status="Scheduled",
            base_price=100.00
        )
        self.passenger = Passenger.objects.create(
            first_name="Alice",
            document_number="98765432",
            email="alice@example.com",
            date_of_birth="1988-11-11",
            document_type="DNI"
        )
        self.seat = Seat.objects.create(
            airplane=self.airplane,
            number="2B",
            row=2,
            column="B",
            type="ECO",
            status="Available"
        )

    def test_create_reservation(self):
        reservation = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            status="PEN",
            price=120.00,
            reservation_code="RES12345"
        )
        self.assertEqual(reservation.status, "PEN")
        self.assertEqual(reservation.price, 120.00)
        self.assertEqual(str(reservation), f"Reservation RES12345 for Alice on flight {self.flight.id}")

    def test_reservation_seat_status_update_confirmed(self):
        reservation = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            status="PEN",
            price=120.00,
            reservation_code="RES12346"
        )
        reservation.status = "CON"
        reservation.save()
        self.seat.refresh_from_db()
        self.assertEqual(self.seat.status, "Reserved")

    def test_reservation_seat_status_update_cancelled(self):
        self.seat.status = "Reserved"
        self.seat.save()
        reservation = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            status="CON",
            price=120.00,
            reservation_code="RES12347"
        )
        reservation.status = "CAN"
        reservation.save()
        self.seat.refresh_from_db()
        self.assertEqual(self.seat.status, "Available")

    def test_reservation_clean_confirmed_invalid_seat_status(self):
        self.seat.status = "Available"
        self.seat.save()
        reservation = Reservation(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            status="CON",
            price=120.00,
            reservation_code="RES12348"
        )
        with self.assertRaisesMessage(Exception, 'The seat must be in "Reserved" or "Occupied" status for a confirmed/paid reservation.'):
            reservation.full_clean()

    def test_reservation_clean_cancelled_invalid_seat_status(self):
        self.seat.status = "Reserved"
        self.seat.save()
        reservation = Reservation(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            status="CAN",
            price=120.00,
            reservation_code="RES12349"
        )
        with self.assertRaisesMessage(Exception, 'The seat must be in "Available" status for a cancelled reservation.'):
            reservation.full_clean()

class UserProfileModelTest(TestCase):
    def test_create_user_profile(self):
        user_profile = UserProfile.objects.create(
            username="testuser",
            password="testpassword", # In a real app, this would be hashed
            email="test@example.com",
            role="CLI"
        )
        self.assertEqual(user_profile.username, "testuser")
        self.assertEqual(user_profile.email, "test@example.com")
        self.assertEqual(str(user_profile), "testuser")

class TicketModelTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(model="Cessna 172", capacity=4, rows=1, columns=4)
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            origin="SFO",
            destination="LAX",
            departure_date=timezone.now() + timedelta(days=3),
            arrival_date=timezone.now() + timedelta(days=3, hours=1),
            duration=timedelta(hours=1),
            status="Scheduled",
            base_price=75.00
        )
        self.passenger = Passenger.objects.create(
            first_name="Bob",
            document_number="11223344",
            email="bob@example.com",
            date_of_birth="1970-02-02",
            document_type="PAS"
        )
        self.seat = Seat.objects.create(
            airplane=self.airplane,
            number="1C",
            row=1,
            column="C",
            type="ECO",
            status="Reserved"
        )
        self.reservation = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            status="CON",
            price=80.00,
            reservation_code="TKT54321"
        )

    def test_create_ticket(self):
        ticket = Ticket.objects.create(
            reservation=self.reservation,
            barcode="BARCODE12345",
            status="EMI"
        )
        self.assertEqual(ticket.barcode, "BARCODE12345")
        self.assertEqual(ticket.status, "EMI")
        self.assertEqual(str(ticket), f"Ticket BARCODE12345 for reservation {self.reservation.reservation_code}")

class RegistrationViewTest(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/register.html')

    def test_user_registration_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'VeryStrongPassword123!@#',
            'password2': 'VeryStrongPassword123!@#',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        if response.status_code != 302:
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")
            if 'form' in response.context:
                print(f"Form errors: {response.context['form'].errors}")
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_user_registration_invalid_form(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'invalid-email', # Invalid email
            'password1': 'VeryStrongPassword123!@#',
            'password2': 'VeryStrongPassword123!@#',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
        self.assertFormError(response.context['form'], 'email', 'Enter a valid email address.')

    def test_user_registration_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password1': 'VeryStrongPassword123!@#',
            'password2': 'DifferentPassword456!', # Mismatched passwords
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser2').exists())
        self.assertFormError(response.context['form'], 'password2', 'The two password fields didn’t match.')

class HomeViewTest(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/home.html')

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
