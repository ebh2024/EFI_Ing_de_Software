from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
import uuid
from airline.models import Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket, Seat
from airline.serializers import SeatSerializer
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

class AirplaneViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.seat_layout = SeatLayout.objects.create(layout_name='Test Layout', rows=5, columns=5)
        self.airplane_data = {'registration_number': 'N12345', 'manufacturer': 'Boeing', 'model_name': '747', 'capacity': 100, 'seat_layout': self.seat_layout.pk}
        # Ensure the airplane created in setUp has a unique registration number different from self.airplane_data
        self.airplane = Airplane.objects.create(seat_layout=self.seat_layout, registration_number='SETUP_N' + str(uuid.uuid4())[:5], manufacturer='Boeing', model_name='747', capacity=100)
        self.list_url = reverse('airplane-list')
        self.detail_url = reverse('airplane-detail', kwargs={'pk': self.airplane.pk})

    @patch('airline.services.AirplaneService.create_airplane_with_seats')
    def test_create_airplane(self, mock_create_airplane_with_seats):
        mock_create_airplane_with_seats.return_value = self.airplane
        # Modify airplane_data to have a unique registration_number for this test
        unique_airplane_data = self.airplane_data.copy()
        unique_airplane_data['registration_number'] = 'TEST_N' + str(uuid.uuid4())[:5]
        response = self.client.post(self.list_url, unique_airplane_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create_airplane_with_seats.assert_called_once()

    @patch('airline.services.AirplaneService.update_airplane')
    def test_update_airplane(self, mock_update_airplane):
        updated_data = {'registration_number': 'N54321'}
        mock_update_airplane.return_value = self.airplane
        response = self.client.patch(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_airplane.assert_called_once()

    @patch('airline.services.AirplaneService.delete_airplane')
    def test_delete_airplane(self, mock_delete_airplane):
        mock_delete_airplane.return_value = True
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_airplane.assert_called_once()

class FlightViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.airplane = Airplane.objects.create(registration_number='N12345', manufacturer='Boeing', model_name='747', capacity=100)
        self.flight_data = {
            'origin': 'JFK',
            'destination': 'LAX',
            'departure_date': datetime.now().isoformat(),
            'arrival_date': (datetime.now() + timedelta(hours=3)).isoformat(),
            'duration': str(timedelta(hours=3)),
            'status': 'Scheduled',
            'base_price': 100.00,
            'airplane': self.airplane.pk
        }
        self.flight = Flight.objects.create(
            origin='JFK',
            destination='LAX',
            departure_date=datetime.now(),
            arrival_date=datetime.now() + timedelta(hours=3),
            duration=timedelta(hours=3),
            status='Scheduled',
            base_price=100.00,
            airplane=self.airplane
        )
        self.list_url = reverse('flight-list')
        self.detail_url = reverse('flight-detail', kwargs={'pk': self.flight.pk})

    @patch('airline.services.FlightService.create_flight')
    def test_create_flight(self, mock_create_flight):
        mock_create_flight.return_value = self.flight
        response = self.client.post(self.list_url, self.flight_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create_flight.assert_called_once()

    @patch('airline.services.FlightService.update_flight')
    def test_update_flight(self, mock_update_flight):
        updated_data = {'flight_number': 'FL202'}
        mock_update_flight.return_value = self.flight
        response = self.client.patch(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_flight.assert_called_once()

    @patch('airline.services.FlightService.delete_flight')
    def test_delete_flight(self, mock_delete_flight):
        mock_delete_flight.return_value = True
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_flight.assert_called_once()

    @patch('airline.services.FlightService.get_available_seats')
    def test_available_seats(self, mock_get_available_seats):
        # Create actual model instances for mocking
        seat_type_economy = SeatType.objects.create(name='Economy', code='ECO', price_multiplier=1.0)
        seat_1A = Seat.objects.create(
            airplane=self.airplane,
            number='1A',
            row=1,
            column='A',
            seat_type=seat_type_economy,
            status='Available'
        )
        mock_get_available_seats.return_value = [seat_1A]

        response = self.client.get(reverse('flight-available-seats', kwargs={'pk': self.flight.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['number'], '1A') # Changed from 'seat_number' to 'number' as per Seat model field
        mock_get_available_seats.assert_called_once_with(str(self.flight.pk))

class PassengerViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        # Create a unique passenger for setUp
        self.passenger = Passenger.objects.create(
            first_name='Setup', last_name='Passenger', email='setup@example.com',
            date_of_birth='1985-05-05', document_number='SETUP12345', document_type='PAS'
        )
        self.list_url = reverse('passenger-list')
        self.detail_url = reverse('passenger-detail', kwargs={'pk': self.passenger.pk})

    @patch('airline.services.PassengerService.create_passenger')
    def test_create_passenger(self, mock_create_passenger):
        # Use unique data for the test_create_passenger
        unique_passenger_data = {
            'first_name': 'Test', 'last_name': 'User', 'email': 'test.user@example.com',
            'date_of_birth': '1990-01-01', 'document_number': 'UNIQUE98765', 'document_type': 'DNI'
        }
        mock_create_passenger.return_value = Passenger(**unique_passenger_data) # Mock return value should be an object
        response = self.client.post(self.list_url, unique_passenger_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create_passenger.assert_called_once()

    @patch('airline.services.PassengerService.update_passenger')
    def test_update_passenger(self, mock_update_passenger):
        updated_data = {'first_name': 'Jane'}
        mock_update_passenger.return_value = self.passenger
        response = self.client.patch(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_passenger.assert_called_once()

    @patch('airline.services.PassengerService.delete_passenger')
    def test_delete_passenger(self, mock_delete_passenger):
        mock_delete_passenger.return_value = True
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_passenger.assert_called_once()

class ReservationViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.airplane = Airplane.objects.create(registration_number='N12345', manufacturer='Boeing', model_name='747', capacity=100)
        self.flight = Flight.objects.create(
            origin='JFK',
            destination='LAX',
            departure_date=datetime.now(),
            arrival_date=datetime.now() + timedelta(hours=3),
            duration=timedelta(hours=3),
            status='Scheduled',
            base_price=100.00,
            airplane=self.airplane
        )
        self.passenger = Passenger.objects.create(first_name='John', last_name='Doe', email='john.doe@example.com', date_of_birth='1990-01-01', document_number='123456789')
        self.seat_type = SeatType.objects.create(name='Economy', price_multiplier=1.0, code='ECO')
        self.seat_layout = SeatLayout.objects.create(layout_name='747 Layout', rows=10, columns=10)
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout,
            row=1,
            column='A',
            seat_type=self.seat_type
        )
        # Create a Seat object for the reservation
        self.seat = Seat.objects.create(
            airplane=self.airplane,
            number='1A',
            row=1,
            column='A',
            seat_type=self.seat_type,
            status='Available'
        )
        self.reservation_data = {
            'flight': self.flight.pk,
            'passenger': self.passenger.pk,
            'seat': self.seat.pk,
            'price': 150.00
        }
        self.reservation = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            price=150.00,
            status='PEN',
            reservation_code='RES123'
        )
        self.list_url = reverse('reservation-list')
        self.detail_url = reverse('reservation-detail', kwargs={'pk': self.reservation.pk})

    @patch('airline.services.ReservationService.create_reservation')
    def test_create_reservation(self, mock_create_reservation):
        mock_create_reservation.return_value = self.reservation
        response = self.client.post(self.list_url, self.reservation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create_reservation.assert_called_once()

    def test_create_reservation_missing_fields(self):
        response = self.client.post(self.list_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required fields', response.data['detail'])

    @patch('airline.services.ReservationService.update_reservation')
    def test_update_reservation(self, mock_update_reservation):
        updated_data = {
            'flight': self.reservation.flight,
            'passenger': self.reservation.passenger,
            'seat': self.reservation.seat,
            'price': self.reservation.price,
            'status': 'CON'
        }
        mock_update_reservation.return_value = self.reservation
        response = self.client.patch(self.detail_url, {
            'flight': self.reservation.flight.pk,
            'passenger': self.reservation.passenger.pk,
            'seat': self.reservation.seat.pk,
            'price': str(self.reservation.price),
            'status': 'CON'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_reservation.assert_called_once_with(self.reservation.pk, updated_data)

    @patch('airline.services.ReservationService.delete_reservation')
    def test_delete_reservation(self, mock_delete_reservation):
        mock_delete_reservation.return_value = True
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_reservation.assert_called_once()

    @patch('airline.services.ReservationService.confirm_reservation')
    def test_confirm_reservation(self, mock_confirm_reservation):
        mock_confirm_reservation.return_value = self.reservation
        response = self.client.post(reverse('reservation-confirm', kwargs={'pk': self.reservation.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_confirm_reservation.assert_called_once_with(str(self.reservation.pk))

    @patch('airline.services.ReservationService.cancel_reservation')
    def test_cancel_reservation(self, mock_cancel_reservation):
        mock_cancel_reservation.return_value = self.reservation
        response = self.client.post(reverse('reservation-cancel', kwargs={'pk': self.reservation.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_cancel_reservation.assert_called_once_with(str(self.reservation.pk))

class SeatLayoutViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.seat_layout_data = {'layout_name': 'Test Layout', 'rows': 5, 'columns': 5}
        self.seat_layout = SeatLayout.objects.create(**self.seat_layout_data)
        self.list_url = reverse('seatlayout-list')
        self.detail_url = reverse('seatlayout-detail', kwargs={'pk': self.seat_layout.pk})

    @patch('airline.services.SeatLayoutService.create_seat_layout_with_positions')
    def test_create_seat_layout(self, mock_create_seat_layout_with_positions):
        mock_create_seat_layout_with_positions.return_value = self.seat_layout
        response = self.client.post(self.list_url, self.seat_layout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create_seat_layout_with_positions.assert_called_once()

    def test_create_seat_layout_missing_fields(self):
        response = self.client.post(self.list_url, {'layout_name': 'Incomplete'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required fields', response.data['detail'])

    @patch('airline.services.SeatLayoutService.update_seat_layout')
    def test_update_seat_layout(self, mock_update_seat_layout):
        updated_data = {'layout_name': 'Updated Layout'}
        mock_update_seat_layout.return_value = self.seat_layout
        response = self.client.patch(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_seat_layout.assert_called_once()

    @patch('airline.services.SeatLayoutService.delete_seat_layout')
    def test_delete_seat_layout(self, mock_delete_seat_layout):
        mock_delete_seat_layout.return_value = True
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_seat_layout.assert_called_once()

class SeatTypeViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        # Create a unique seat type for setUp
        self.seat_type = SeatType.objects.create(name='Setup Economy', code='SEC', price_multiplier=1.0)
        self.list_url = reverse('seattype-list')
        self.detail_url = reverse('seattype-detail', kwargs={'pk': self.seat_type.pk})

    @patch('airline.services.SeatTypeService.create_seat_type')
    def test_create_seat_type(self, mock_create_seat_type):
        # Use unique data for the test_create_seat_type
        unique_seat_type_data = {'name': 'New Economy', 'code': 'NEC', 'price_multiplier': 1.0}
        mock_create_seat_type.return_value = SeatType(**unique_seat_type_data) # Mock return value should be an object
        response = self.client.post(self.list_url, unique_seat_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create_seat_type.assert_called_once()

    @patch('airline.services.SeatTypeService.update_seat_type')
    def test_update_seat_type(self, mock_update_seat_type):
        updated_data = {'name': 'Business'}
        mock_update_seat_type.return_value = self.seat_type
        response = self.client.patch(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_seat_type.assert_called_once()

    @patch('airline.services.SeatTypeService.delete_seat_type')
    def test_delete_seat_type(self, mock_delete_seat_type):
        mock_delete_seat_type.return_value = True
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_seat_type.assert_called_once()

class SeatLayoutPositionViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.seat_type = SeatType.objects.create(name='Economy', price_multiplier=1.0, code='ECO')
        self.seat_layout = SeatLayout.objects.create(layout_name='Test Layout', rows=5, columns=5)
        self.seat_layout_position_data = {
            'seat_layout': self.seat_layout.pk,
            'row': 1,
            'column': 'A',
            'seat_type': self.seat_type.pk
        }
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout,
            row=1,
            column='A',
            seat_type=self.seat_type
        )
        self.list_url = reverse('seatlayoutposition-list')
        self.detail_url = reverse('seatlayoutposition-detail', kwargs={'pk': self.seat_layout_position.pk})

    def test_create_seat_layout_position(self):
        unique_seat_layout_position_data = {
            'seat_layout': self.seat_layout.pk,
            'row': 2, # Use a unique row
            'column': 'B', # Use a unique column
            'seat_type': self.seat_type.pk
        }
        response = self.client.post(self.list_url, unique_seat_layout_position_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SeatLayoutPosition.objects.count(), 2)

    def test_retrieve_seat_layout_position(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seat_number'], '1A')

    def test_update_seat_layout_position(self):
        updated_data = {'row': 1, 'column': 'B'}
        response = self.client.patch(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.seat_layout_position.refresh_from_db()
        self.assertEqual(self.seat_layout_position.seat_number, '1B')

    def test_delete_seat_layout_position(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SeatLayoutPosition.objects.count(), 0)

class FlightHistoryViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.airplane = Airplane.objects.create(registration_number='N12345', manufacturer='Boeing', model_name='747', capacity=100)
        self.flight = Flight.objects.create(
            origin='JFK',
            destination='LAX',
            departure_date=datetime.now(),
            arrival_date=datetime.now() + timedelta(hours=3),
            duration=timedelta(hours=3),
            status='Scheduled',
            base_price=100.00,
            airplane=self.airplane
        )
        self.passenger = Passenger.objects.create(first_name='John', last_name='Doe', email='john.doe@example.com', date_of_birth='1990-01-01', document_number='123456789')
        self.seat_type = SeatType.objects.create(name='Economy', price_multiplier=1.0, code='ECO')
        self.seat_layout = SeatLayout.objects.create(layout_name='747 Layout', rows=10, columns=10)
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout,
            row=1,
            column='A',
            seat_type=self.seat_type
        )
        self.flight_history = FlightHistory.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat_number='1A',
            price_paid=150.00
        )
        self.list_url = reverse('flighthistory-list')
        self.detail_url = reverse('flighthistory-detail', kwargs={'pk': self.flight_history.pk})

    def test_list_flight_history(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_flight_history(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seat_number'], '1A')

    @patch('airline.services.FlightHistoryService.get_flight_history_by_passenger')
    def test_by_passenger(self, mock_get_flight_history_by_passenger):
        mock_get_flight_history_by_passenger.return_value = [self.flight_history]
        response = self.client.get(reverse('flighthistory-by-passenger'), {'passenger_id': self.passenger.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        mock_get_flight_history_by_passenger.assert_called_once_with(str(self.passenger.pk))

    def test_by_passenger_missing_id(self):
        response = self.client.get(reverse('flighthistory-by-passenger'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passenger ID is required', response.data['detail'])

    @patch('airline.services.FlightHistoryService.get_flight_history_by_flight')
    def test_by_flight(self, mock_get_flight_history_by_flight):
        mock_get_flight_history_by_flight.return_value = [self.flight_history]
        response = self.client.get(reverse('flighthistory-by-flight'), {'flight_id': self.flight.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        mock_get_flight_history_by_flight.assert_called_once_with(str(self.flight.pk))

    def test_by_flight_missing_id(self):
        response = self.client.get(reverse('flighthistory-by-flight'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Flight ID is required', response.data['detail'])

class TicketViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.airplane = Airplane.objects.create(registration_number='N12345', manufacturer='Boeing', model_name='747', capacity=100)
        self.flight = Flight.objects.create(
            origin='JFK',
            destination='LAX',
            departure_date=datetime.now(),
            arrival_date=datetime.now() + timedelta(hours=3),
            duration=timedelta(hours=3),
            status='Scheduled',
            base_price=100.00,
            airplane=self.airplane
        )
        self.passenger = Passenger.objects.create(first_name='John', last_name='Doe', email='john.doe@example.com', date_of_birth='1990-01-01', document_number='123456789')
        self.seat_type = SeatType.objects.create(name='Economy', price_multiplier=1.0, code='ECO')
        self.seat_layout = SeatLayout.objects.create(layout_name='747 Layout', rows=10, columns=10)
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout,
            row=1,
            column='A',
            seat_type=self.seat_type
        )
        self.seat = Seat.objects.create(
            airplane=self.airplane,
            number='1A',
            row=1,
            column='A',
            seat_type=self.seat_type,
            status='Available'
        )
        self.reservation = Reservation.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat=self.seat,
            price=150.00,
            status='CON',
            reservation_code='RES123'
        )
        self.ticket = Ticket.objects.create(
            reservation=self.reservation,
            barcode='TKT12345',
            issue_date=datetime.now(),
            status='EMI'
        )
        self.list_url = reverse('ticket-list')
        self.detail_url = reverse('ticket-detail', kwargs={'pk': self.ticket.pk})

    def test_list_tickets(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_ticket(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ticket_number'], 'TKT12345')

    @patch('airline.services.TicketService.delete_ticket')
    def test_delete_ticket(self, mock_delete_ticket):
        mock_delete_ticket.return_value = True
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_ticket.assert_called_once()

    @patch('airline.services.TicketService.issue_ticket')
    def test_issue_ticket(self, mock_issue_ticket):
        mock_issue_ticket.return_value = self.ticket
        response = self.client.post(reverse('ticket-issue', kwargs={'pk': self.reservation.pk}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_issue_ticket.assert_called_once_with(str(self.reservation.pk))

    @patch('airline.services.TicketService.cancel_ticket')
    def test_cancel_ticket(self, mock_cancel_ticket):
        mock_cancel_ticket.return_value = self.ticket
        response = self.client.post(reverse('ticket-cancel', kwargs={'pk': self.ticket.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_cancel_ticket.assert_called_once_with(str(self.ticket.pk))
