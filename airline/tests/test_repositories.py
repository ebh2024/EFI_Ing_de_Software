from django.test import TestCase
from django.db.models import Model
from django.shortcuts import get_object_or_404
from unittest.mock import patch, MagicMock

from airline.models import Airplane, Flight, Passenger, Reservation, Seat, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket
from airline.repositories import (
    BaseRepository, AirplaneRepository, FlightRepository, PassengerRepository,
    ReservationRepository, SeatRepository, SeatLayoutRepository, SeatTypeRepository,
    SeatLayoutPositionRepository, FlightHistoryRepository, TicketRepository
)

class MockModel(Model):
    """A mock Django model for testing BaseRepository."""
    class Meta:
        app_label = 'airline' # Required for mock models

    def __init__(self, id=None, **kwargs):
        super().__init__()
        self.id = id
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def objects(cls):
        return MockQuerySet(cls)

class MockQuerySet:
    """A mock Django QuerySet for testing BaseRepository."""
    def __init__(self, model):
        self.model = model
        self.data = []

    def all(self):
        return self.data

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.id = len(self.data) + 1 # Simulate ID assignment
        self.data.append(obj)
        return obj

    def filter(self, **kwargs):
        filtered_data = [
            obj for obj in self.data
            if all(getattr(obj, k) == v for k, v in kwargs.items())
        ]
        return MockQuerySet(self.model)._set_data(filtered_data)

    def get_or_create(self, defaults=None, **kwargs):
        filtered_data = self.filter(**kwargs).all()
        if filtered_data:
            return filtered_data[0], False
        else:
            obj = self.create(**{**kwargs, **(defaults or {})})
            return obj, True

    def select_related(self, *fields):
        return self

    def order_by(self, *fields):
        return self

    def _set_data(self, data):
        self.data = data
        return self

class BaseRepositoryTests(TestCase):
    def setUp(self):
        self.repository = BaseRepository()
        self.repository.model = MockModel # Use a mock model for BaseRepository tests

    @patch('airline.repositories.get_object_or_404')
    def test_get_by_id(self, mock_get_object_or_404):
        mock_instance = MagicMock(id=1)
        mock_get_object_or_404.return_value = mock_instance
        result = self.repository.get_by_id(1)
        mock_get_object_or_404.assert_called_once_with(self.repository.model, pk=1)
        self.assertEqual(result, mock_instance)

    def test_get_all(self):
        with patch.object(self.repository.model.objects, 'all', return_value=['obj1', 'obj2']) as mock_all:
            result = self.repository.get_all()
            mock_all.assert_called_once()
            self.assertEqual(result, ['obj1', 'obj2'])

    def test_create(self):
        with patch.object(self.repository.model.objects, 'create', return_value='new_obj') as mock_create:
            result = self.repository.create({'name': 'test'})
            mock_create.assert_called_once_with(name='test')
            self.assertEqual(result, 'new_obj')

    def test_update(self):
        mock_obj = MagicMock(id=1, name='old_name')
        with patch('airline.repositories.get_object_or_404', return_value=mock_obj) as mock_get:
            result = self.repository.update(1, {'name': 'new_name'})
            mock_get.assert_called_once_with(self.repository.model, pk=1)
            self.assertEqual(mock_obj.name, 'new_name')
            mock_obj.save.assert_called_once()
            self.assertEqual(result, mock_obj)

    def test_delete(self):
        mock_obj = MagicMock(id=1)
        with patch('airline.repositories.get_object_or_404', return_value=mock_obj) as mock_get:
            result = self.repository.delete(1)
            mock_get.assert_called_once_with(self.repository.model, pk=1)
            mock_obj.delete.assert_called_once()
            self.assertTrue(result)

class AirplaneRepositoryTests(TestCase):
    def setUp(self):
        self.repository = AirplaneRepository()

    def test_model_is_airplane(self):
        self.assertEqual(self.repository.model, Airplane)

class PassengerRepositoryTests(TestCase):
    def setUp(self):
        self.repository = PassengerRepository()

    def test_model_is_passenger(self):
        self.assertEqual(self.repository.model, Passenger)

    @patch.object(Passenger.objects, 'get_or_create')
    def test_get_or_create_passenger(self, mock_get_or_create):
        mock_passenger = MagicMock(email='test@example.com')
        mock_get_or_create.return_value = (mock_passenger, True)
        email = 'test@example.com'
        defaults = {'first_name': 'Test', 'last_name': 'User'}
        result, created = self.repository.get_or_create_passenger(email, defaults)
        mock_get_or_create.assert_called_once_with(email=email, defaults=defaults)
        self.assertEqual(result, mock_passenger)
        self.assertTrue(created)

class ReservationRepositoryTests(TestCase):
    def setUp(self):
        self.repository = ReservationRepository()

    def test_model_is_reservation(self):
        self.assertEqual(self.repository.model, Reservation)

    @patch.object(Reservation.objects, 'filter')
    def test_filter_by_flight_seat_status(self, mock_filter):
        mock_flight = MagicMock(id=1)
        mock_seat = MagicMock(id=1)
        statuses = ['CONFIRMED', 'PENDING']
        self.repository.filter_by_flight_seat_status(mock_flight, mock_seat, statuses)
        mock_filter.assert_called_once_with(flight=mock_flight, seat=mock_seat, status__in=statuses)

    @patch.object(Reservation.objects, 'filter')
    def test_filter_by_flight_and_select_related(self, mock_filter):
        mock_flight = MagicMock(id=1)
        mock_filter.return_value.select_related.return_value = ['res1', 'res2']
        result = self.repository.filter_by_flight_and_select_related(mock_flight)
        mock_filter.assert_called_once_with(flight=mock_flight)
        mock_filter.return_value.select_related.assert_called_once_with('passenger', 'seat')
        self.assertEqual(result, ['res1', 'res2'])

class SeatRepositoryTests(TestCase):
    def setUp(self):
        self.repository = SeatRepository()

    def test_model_is_seat(self):
        self.assertEqual(self.repository.model, Seat)

    @patch.object(Seat.objects, 'filter')
    def test_filter_by_airplane_ordered(self, mock_filter):
        mock_airplane = MagicMock(id=1)
        self.repository.filter_by_airplane_ordered(mock_airplane)
        mock_filter.assert_called_once_with(airplane=mock_airplane)
        mock_filter.return_value.order_by.assert_called_once_with('row', 'column')

class FlightHistoryRepositoryTests(TestCase):
    def setUp(self):
        self.repository = FlightHistoryRepository()

    def test_model_is_flighthistory(self):
        self.assertEqual(self.repository.model, FlightHistory)

    @patch.object(FlightHistory.objects, 'filter')
    def test_filter_by_passenger_ordered(self, mock_filter):
        mock_passenger = MagicMock(id=1)
        self.repository.filter_by_passenger_ordered(mock_passenger)
        mock_filter.assert_called_once_with(passenger=mock_passenger)
        mock_filter.return_value.order_by.assert_called_once_with('-booking_date')

    @patch.object(FlightHistory.objects, 'filter')
    def test_filter_by_flight(self, mock_filter):
        self.repository.filter_by_flight(1)
        mock_filter.assert_called_once_with(flight__id=1)

    @patch.object(FlightHistory.objects, 'filter')
    def test_filter_by_passenger(self, mock_filter):
        self.repository.filter_by_passenger(1)
        mock_filter.assert_called_once_with(passenger__id=1)

class TicketRepositoryTests(TestCase):
    def setUp(self):
        self.repository = TicketRepository()

    def test_model_is_ticket(self):
        self.assertEqual(self.repository.model, Ticket)

    @patch.object(Ticket.objects, 'get_or_create')
    def test_get_or_create_ticket(self, mock_get_or_create):
        mock_reservation = MagicMock(id=1)
        mock_get_or_create.return_value = (MagicMock(), True)
        defaults = {'price': 100}
        result, created = self.repository.get_or_create_ticket(mock_reservation, defaults)
        mock_get_or_create.assert_called_once_with(reservation=mock_reservation, defaults=defaults)
        self.assertTrue(created)

# Add similar tests for other repositories (FlightRepository, SeatLayoutRepository, SeatTypeRepository, SeatLayoutPositionRepository)
# These repositories only inherit BaseRepository and don't add custom methods, so testing their model attribute is sufficient.
class FlightRepositoryTests(TestCase):
    def setUp(self):
        self.repository = FlightRepository()

    def test_model_is_flight(self):
        self.assertEqual(self.repository.model, Flight)

class SeatLayoutRepositoryTests(TestCase):
    def setUp(self):
        self.repository = SeatLayoutRepository()

    def test_model_is_seatlayout(self):
        self.assertEqual(self.repository.model, SeatLayout)

class SeatTypeRepositoryTests(TestCase):
    def setUp(self):
        self.repository = SeatTypeRepository()

    def test_model_is_seattype(self):
        self.assertEqual(self.repository.model, SeatType)

class SeatLayoutPositionRepositoryTests(TestCase):
    def setUp(self):
        self.repository = SeatLayoutPositionRepository()

    def test_model_is_seatlayoutposition(self):
        self.assertEqual(self.repository.model, SeatLayoutPosition)
