from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from airline.models import Airplane, Flight, Passenger, FlightHistory, Seat, Reservation, Ticket

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

class FlightManagementViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpassword')
        self.client.login(username='admin', password='adminpassword')

        self.airplane = Airplane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)
        self.departure_date = timezone.now() + timedelta(days=1)
        self.arrival_date = self.departure_date + timedelta(hours=3)
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            origin="EZE",
            destination="MIA",
            departure_date=self.departure_date,
            arrival_date=self.arrival_date,
            duration=timedelta(hours=3),
            status="Scheduled",
            base_price=500.00
        )

    def test_flight_list_view(self):
        response = self.client.get(reverse('flight_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/flight_list.html')
        self.assertContains(response, self.flight.origin)

    def test_flight_create_view_get(self):
        response = self.client.get(reverse('flight_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/flight_form.html')
        self.assertContains(response, 'Create')

    def test_flight_create_view_post_success(self):
        new_departure_date = timezone.now() + timedelta(days=5)
        new_arrival_date = new_departure_date + timedelta(hours=2)
        response = self.client.post(reverse('flight_create'), {
            'airplane': self.airplane.id,
            'origin': 'COR',
            'destination': 'SCL',
            'departure_date': new_departure_date.strftime('%Y-%m-%dT%H:%M'),
            'arrival_date': new_arrival_date.strftime('%Y-%m-%dT%H:%M'),
            'duration': '02:00:00',
            'status': 'Scheduled',
            'base_price': '250.00'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('flight_list'))
        self.assertTrue(Flight.objects.filter(origin='COR', destination='SCL').exists())

    def test_flight_create_view_post_invalid(self):
        response = self.client.post(reverse('flight_create'), {
            'airplane': self.airplane.id,
            'origin': 'COR',
            'destination': 'SCL',
            'departure_date': (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'), # Past date
            'arrival_date': (timezone.now() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'), # Before departure
            'duration': '02:00:00',
            'status': 'Scheduled',
            'base_price': '250.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'departure_date', 'Departure date cannot be in the past.')
        self.assertFormError(response.context['form'], 'arrival_date', 'Arrival date must be after departure date.')

    def test_flight_update_view_get(self):
        response = self.client.get(reverse('flight_update', args=[self.flight.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/flight_form.html')
        self.assertContains(response, 'Update')
        self.assertContains(response, self.flight.origin)

    def test_flight_update_view_post_success(self):
        updated_destination = "LAX"
        response = self.client.post(reverse('flight_update', args=[self.flight.pk]), {
            'airplane': self.airplane.id,
            'origin': self.flight.origin,
            'destination': updated_destination,
            'departure_date': self.flight.departure_date.strftime('%Y-%m-%dT%H:%M'),
            'arrival_date': self.flight.arrival_date.strftime('%Y-%m-%dT%H:%M'),
            'duration': self.flight.duration,
            'status': 'Delayed',
            'base_price': '550.00'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('flight_list'))
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.destination, updated_destination)
        self.assertEqual(self.flight.status, 'Delayed')

    def test_flight_update_view_post_invalid(self):
        response = self.client.post(reverse('flight_update', args=[self.flight.pk]), {
            'airplane': self.airplane.id,
            'origin': self.flight.origin,
            'destination': self.flight.destination,
            'departure_date': (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'), # Past date
            'arrival_date': (timezone.now() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'), # Before departure
            'duration': self.flight.duration,
            'status': 'Scheduled',
            'base_price': '500.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'departure_date', 'Departure date cannot be in the past.')
        self.assertFormError(response.context['form'], 'arrival_date', 'Arrival date must be after departure date.')

    def test_flight_delete_view_get(self):
        response = self.client.get(reverse('flight_delete', args=[self.flight.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/flight_confirm_delete.html')
        self.assertContains(response, self.flight.origin)

    def test_flight_delete_view_post_success(self):
        flight_id = self.flight.pk
        response = self.client.post(reverse('flight_delete', args=[flight_id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('flight_list'))
        self.assertFalse(Flight.objects.filter(pk=flight_id).exists())

class PassengerManagementViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpassword')
        self.client.login(username='admin', password='adminpassword')
        self.passenger = Passenger.objects.create(
            first_name="Jane",
            last_name="Doe",
            document_number="123456789",
            email="jane.doe@example.com",
            date_of_birth=timezone.datetime(1990, 1, 1).date(),
            document_type="DNI"
        )
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
        self.flight_history = FlightHistory.objects.create(
            passenger=self.passenger,
            flight=self.flight,
            booking_date=timezone.now(),
            seat_number="10A",
            price_paid=500.00
        )

    def test_passenger_list_view(self):
        response = self.client.get(reverse('passenger_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/passenger_list.html')
        self.assertContains(response, self.passenger.first_name)
        self.assertContains(response, self.passenger.last_name)

    def test_passenger_create_view_get(self):
        response = self.client.get(reverse('passenger_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/passenger_form.html')
        self.assertContains(response, 'Create')

    def test_passenger_create_view_post_success(self):
        response = self.client.post(reverse('passenger_create'), {
            'first_name': 'New',
            'last_name': 'Passenger',
            'document_number': '987654321',
            'email': 'new.passenger@example.com',
            'date_of_birth': '1985-03-15',
            'document_type': 'PAS'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('passenger_list'))
        self.assertTrue(Passenger.objects.filter(first_name='New', last_name='Passenger').exists())

    def test_passenger_create_view_post_invalid(self):
        response = self.client.post(reverse('passenger_create'), {
            'first_name': 'Invalid',
            'last_name': 'Email',
            'document_number': '112233445',
            'email': 'invalid-email', # Invalid email
            'date_of_birth': '1990-01-01',
            'document_type': 'DNI'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'Enter a valid email address.')

    def test_passenger_update_view_get(self):
        response = self.client.get(reverse('passenger_update', args=[self.passenger.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/passenger_form.html')
        self.assertContains(response, 'Update')
        self.assertContains(response, self.passenger.first_name)

    def test_passenger_update_view_post_success(self):
        updated_email = "jane.updated@example.com"
        response = self.client.post(reverse('passenger_update', args=[self.passenger.pk]), {
            'first_name': self.passenger.first_name,
            'last_name': self.passenger.last_name,
            'document_number': self.passenger.document_number,
            'email': updated_email,
            'date_of_birth': self.passenger.date_of_birth,
            'document_type': self.passenger.document_type
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('passenger_list'))
        self.passenger.refresh_from_db()
        self.assertEqual(self.passenger.email, updated_email)

    def test_passenger_update_view_post_invalid(self):
        response = self.client.post(reverse('passenger_update', args=[self.passenger.pk]), {
            'first_name': self.passenger.first_name,
            'last_name': self.passenger.last_name,
            'document_number': self.passenger.document_number,
            'email': 'invalid-email', # Invalid email
            'date_of_birth': self.passenger.date_of_birth,
            'document_type': self.passenger.document_type
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'Enter a valid email address.')

    def test_passenger_delete_view_get(self):
        response = self.client.get(reverse('passenger_delete', args=[self.passenger.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/passenger_confirm_delete.html')
        self.assertContains(response, self.passenger.first_name)

    def test_passenger_delete_view_post_success(self):
        passenger_id = self.passenger.pk
        response = self.client.post(reverse('passenger_delete', args=[passenger_id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('passenger_list'))
        self.assertFalse(Passenger.objects.filter(pk=passenger_id).exists())

    def test_passenger_flight_history_view(self):
        response = self.client.get(reverse('passenger_flight_history', args=[self.passenger.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/passenger_flight_history.html')
        self.assertContains(response, self.passenger.first_name)
        self.assertContains(response, self.flight.origin)
        self.assertContains(response, self.flight.destination)

class ReservationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

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
        # Create a passenger linked to the test user's email
        self.passenger = Passenger.objects.create(
            first_name="Test",
            last_name="Passenger",
            document_number="1122334455",
            email=self.user.email, # Use the test user's email
            date_of_birth="1990-01-01",
            document_type="DNI"
        )
        self.seat_available = Seat.objects.create(
            airplane=self.airplane,
            number="1A",
            row=1,
            column="A",
            type="ECO",
            status="Available"
        )
        self.seat_reserved = Seat.objects.create(
            airplane=self.airplane,
            number="1B",
            row=1,
            column="B",
            type="ECO",
            status="Reserved"
        )
        self.reservation = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat_reserved,
            status="CON",
            price=500.00,
            reservation_code="RESVIEW123"
        )

    def test_flight_detail_with_seats_view(self):
        response = self.client.get(reverse('flight_detail_with_seats', args=[self.flight.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/flight_detail_with_seats.html')
        self.assertContains(response, self.flight.origin)
        self.assertContains(response, self.seat_available.number)
        self.assertContains(response, self.seat_reserved.number)
        self.assertContains(response, 'Reserved') # Check if reserved seat is marked

    def test_reserve_seat_view_get(self):
        response = self.client.get(reverse('reserve_seat', args=[self.flight.pk, self.seat_available.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/reserve_seat.html')
        self.assertContains(response, self.flight.origin)
        self.assertContains(response, self.seat_available.number)

    def test_reserve_seat_view_post_success(self):
        # Create a new flight and seat for this test to avoid unique_together constraint violation
        new_flight = Flight.objects.create(
            airplane=self.airplane,
            origin="BUE",
            destination="RIO",
            departure_date=timezone.now() + timedelta(days=5),
            arrival_date=timezone.now() + timedelta(days=5, hours=4),
            duration=timedelta(hours=4),
            status="Scheduled",
            base_price=300.00
        )
        new_seat = Seat.objects.create(
            airplane=self.airplane,
            number="2C",
            row=2,
            column="C",
            type="ECO",
            status="Available"
        )

        # Ensure the passenger for the logged-in user exists or is created
        Passenger.objects.get_or_create(
            email=self.user.email,
            defaults={'first_name': self.user.username, 'document_number': 'DUMMY12345', 'date_of_birth': '2000-01-01'}
        )
        
        response = self.client.post(reverse('reserve_seat', args=[new_flight.pk, new_seat.pk]), {
            'flight': new_flight.id,
            'seat': new_seat.id,
            'status': 'PEN',
            'price': 300.00
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Reservation.objects.filter(flight=new_flight, seat=new_seat, status='PEN').exists())
        new_seat.refresh_from_db()
        self.assertEqual(new_seat.status, 'Reserved')
        self.assertRedirects(response, reverse('reservation_detail', args=[Reservation.objects.get(flight=new_flight, seat=new_seat).pk]))

    def test_reserve_seat_view_post_already_reserved(self):
        response = self.client.post(reverse('reserve_seat', args=[self.flight.pk, self.seat_reserved.pk]), {
            'flight': self.flight.id,
            'passenger': self.passenger.id,
            'seat': self.seat_reserved.id,
            'status': 'PEN',
            'price': 500.00
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/reservation_error.html')
        self.assertContains(response, 'This seat is already reserved for this flight.')

    def test_reservation_list_view(self):
        response = self.client.get(reverse('reservation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/reservation_list.html')
        self.assertContains(response, self.reservation.reservation_code)

    def test_reservation_detail_view(self):
        response = self.client.get(reverse('reservation_detail', args=[self.reservation.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/reservation_detail.html')
        self.assertContains(response, self.reservation.reservation_code)
        self.assertContains(response, self.reservation.passenger.first_name)

    def test_reservation_update_status_view(self):
        # Test updating to PAID
        response = self.client.get(reverse('reservation_update_status', args=[self.reservation.pk, 'PAID']), follow=True)
        self.assertEqual(response.status_code, 200)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'PAID')
        self.seat_reserved.refresh_from_db()
        self.assertEqual(self.seat_reserved.status, 'Reserved') # Should remain Reserved

        # Test updating to CANCELLED
        response = self.client.get(reverse('reservation_update_status', args=[self.reservation.pk, 'CAN']), follow=True)
        self.assertEqual(response.status_code, 200)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'CAN')
        self.seat_reserved.refresh_from_db()
        self.assertEqual(self.seat_reserved.status, 'Available') # Should become Available

    def test_generate_ticket_view_success(self):
        response = self.client.get(reverse('generate_ticket', args=[self.reservation.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(Ticket.objects.filter(reservation=self.reservation).exists())

    def test_generate_ticket_view_unconfirmed_reservation(self):
        self.reservation.status = 'PEN'
        self.reservation.save()
        response = self.client.get(reverse('generate_ticket', args=[self.reservation.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/reservation_error.html')
        self.assertContains(response, 'Ticket can only be generated for confirmed or paid reservations.')

    def test_ticket_detail_view(self):
        ticket = Ticket.objects.create(
            reservation=self.reservation,
            barcode="TICKET12345",
            status="EMI"
        )
        response = self.client.get(reverse('ticket_detail', args=[ticket.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/ticket_detail.html')
        self.assertContains(response, ticket.barcode)
        self.assertContains(response, self.reservation.reservation_code)
