from django.test import TestCase
from unittest.mock import MagicMock, patch
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid

from airline.services import (
    AirplaneService, FlightService, PassengerService, ReservationService,
    SeatLayoutService, SeatTypeService, SeatLayoutPositionService,
    FlightHistoryService, TicketService
)
from airline.models import (
    Airplane, Flight, Passenger, Seat, Reservation, Ticket, FlightHistory,
    SeatLayout, SeatType, SeatLayoutPosition
)

class BaseServiceTest(TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()

class AirplaneServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = AirplaneService()
        self.service.airplane_repo = self.mock_repo
        self.service.seat_layout_repo = MagicMock()
        self.service.seat_repo = MagicMock()

    def test_create_airplane_with_seats(self):
        mock_seat_layout = MagicMock(spec=SeatLayout)
        mock_seat_layout.id = 1
        mock_seat_layout.rows = 2
        mock_seat_layout.columns = 2
        self.service.seat_layout_repo.get_by_id.return_value = mock_seat_layout

        mock_airplane = MagicMock(spec=Airplane)
        self.mock_repo.create.return_value = mock_airplane

        mock_seat_layout_position = MagicMock(spec=SeatLayoutPosition)
        mock_seat_layout_position.seat_type = MagicMock(spec=SeatType)
        with patch('airline.services.SeatLayoutPosition.objects.filter') as mock_filter:
            mock_filter.return_value.first.return_value = mock_seat_layout_position
            
            data = {'registration_number': 'N123', 'seat_layout': 1}
            airplane = self.service.create_airplane_with_seats(data)

            self.mock_repo.create.assert_called_once_with({
                'registration_number': 'N123',
                'seat_layout': mock_seat_layout
            })
            self.assertEqual(airplane, mock_airplane)
            self.assertEqual(self.service.seat_repo.create.call_count, 4) # 2 rows * 2 columns

    def test_create_airplane_without_seat_layout(self):
        mock_airplane = MagicMock(spec=Airplane)
        self.mock_repo.create.return_value = mock_airplane

        data = {'registration_number': 'N123'}
        airplane = self.service.create_airplane_with_seats(data)

        self.mock_repo.create.assert_called_once_with(data)
        self.assertEqual(airplane, mock_airplane)
        self.service.seat_repo.create.assert_not_called()

    def test_update_airplane(self):
        mock_seat_layout = MagicMock(spec=SeatLayout)
        self.service.seat_layout_repo.get_by_id.return_value = mock_seat_layout
        self.mock_repo.update.return_value = True

        data = {'registration_number': 'N123', 'seat_layout': 1}
        result = self.service.update_airplane(1, data)

        self.service.seat_layout_repo.get_by_id.assert_called_once_with(1)
        self.mock_repo.update.assert_called_once_with(1, {
            'registration_number': 'N123',
            'seat_layout': mock_seat_layout
        })
        self.assertTrue(result)

    def test_delete_airplane(self):
        self.mock_repo.delete.return_value = True
        result = self.service.delete_airplane(1)
        self.mock_repo.delete.assert_called_once_with(1)
        self.assertTrue(result)

class FlightServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = FlightService()
        self.service.flight_repo = self.mock_repo
        self.service.seat_repo = MagicMock()
        self.service.reservation_repo = MagicMock()

    def test_create_flight(self):
        mock_flight = MagicMock(spec=Flight)
        self.mock_repo.create.return_value = mock_flight
        data = {'flight_number': 'FL123'}
        flight = self.service.create_flight(data)
        self.mock_repo.create.assert_called_once_with(data)
        self.assertEqual(flight, mock_flight)

    def test_update_flight(self):
        self.mock_repo.update.return_value = True
        data = {'flight_number': 'FL123'}
        result = self.service.update_flight(1, data)
        self.mock_repo.update.assert_called_once_with(1, data)
        self.assertTrue(result)

    def test_delete_flight(self):
        self.mock_repo.delete.return_value = True
        result = self.service.delete_flight(1)
        self.mock_repo.delete.assert_called_once_with(1)
        self.assertTrue(result)

    def test_get_available_seats(self):
        mock_flight = MagicMock(spec=Flight)
        mock_flight.airplane = MagicMock(spec=Airplane)
        self.mock_repo.get_by_id.return_value = mock_flight

        mock_seat1 = MagicMock(spec=Seat, id=1)
        mock_seat2 = MagicMock(spec=Seat, id=2)
        mock_seat3 = MagicMock(spec=Seat, id=3)
        self.service.seat_repo.filter_by_airplane_ordered.return_value = [mock_seat1, mock_seat2, mock_seat3]

        self.service.reservation_repo.filter_by_flight_seat_status.return_value.values_list.return_value = [2]

        available_seats = self.service.get_available_seats(1)

        self.service.flight_repo.get_by_id.assert_called_once_with(1)
        self.service.seat_repo.filter_by_airplane_ordered.assert_called_once_with(mock_flight.airplane)
        self.service.reservation_repo.filter_by_flight_seat_status.assert_called_once_with(mock_flight, None, ['PEN', 'CON', 'PAID'])
        self.assertEqual(available_seats, [mock_seat1, mock_seat3])

class PassengerServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = PassengerService()
        self.service.passenger_repo = self.mock_repo
        self.service.flight_history_repo = MagicMock()

    def test_create_passenger(self):
        mock_passenger = MagicMock(spec=Passenger)
        self.mock_repo.create.return_value = mock_passenger
        data = {'first_name': 'John'}
        passenger = self.service.create_passenger(data)
        self.mock_repo.create.assert_called_once_with(data)
        self.assertEqual(passenger, mock_passenger)

    def test_update_passenger(self):
        self.mock_repo.update.return_value = True
        data = {'first_name': 'John'}
        result = self.service.update_passenger(1, data)
        self.mock_repo.update.assert_called_once_with(1, data)
        self.assertTrue(result)

    def test_delete_passenger(self):
        self.mock_repo.delete.return_value = True
        result = self.service.delete_passenger(1)
        self.mock_repo.delete.assert_called_once_with(1)
        self.assertTrue(result)

    def test_get_or_create_passenger_for_user_created(self):
        mock_user = MagicMock()
        mock_user.email = 'test@example.com'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.username = 'testuser'

        mock_passenger = MagicMock(spec=Passenger)
        self.service.passenger_repo.get_or_create_passenger.return_value = (mock_passenger, True)

        passenger = self.service.get_or_create_passenger_for_user(mock_user)

        self.service.passenger_repo.get_or_create_passenger.assert_called_once()
        self.assertEqual(passenger, mock_passenger)

    def test_get_or_create_passenger_for_user_existing(self):
        mock_user = MagicMock()
        mock_user.email = 'test@example.com'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.username = 'testuser'

        mock_passenger = MagicMock(spec=Passenger)
        self.service.passenger_repo.get_or_create_passenger.return_value = (mock_passenger, False)

        passenger = self.service.get_or_create_passenger_for_user(mock_user)

        self.service.passenger_repo.get_or_create_passenger.assert_called_once()
        self.assertEqual(passenger, mock_passenger)

    def test_get_passenger_flight_history(self):
        mock_passenger = MagicMock(spec=Passenger)
        self.service.passenger_repo.get_by_id.return_value = mock_passenger
        mock_flight_history = [MagicMock(spec=FlightHistory)]
        self.service.flight_history_repo.filter_by_passenger_ordered.return_value = mock_flight_history

        passenger, flight_history = self.service.get_passenger_flight_history(1)

        self.service.passenger_repo.get_by_id.assert_called_once_with(1)
        self.service.flight_history_repo.filter_by_passenger_ordered.assert_called_once_with(mock_passenger)
        self.assertEqual(passenger, mock_passenger)
        self.assertEqual(flight_history, mock_flight_history)

class ReservationServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = ReservationService()
        self.service.reservation_repo = self.mock_repo
        self.service.flight_repo = MagicMock()
        self.service.passenger_repo = MagicMock()
        self.service.seat_repo = MagicMock()

    @patch('airline.services.transaction.atomic')
    def test_create_reservation_success(self, mock_atomic):
        mock_flight = MagicMock(spec=Flight)
        mock_passenger = MagicMock(spec=Passenger)
        mock_seat = MagicMock(spec=Seat, pk=1)
        mock_reservation = MagicMock(spec=Reservation)

        self.service.flight_repo.get_by_id.return_value = mock_flight
        self.service.passenger_repo.get_by_id.return_value = mock_passenger
        self.service.seat_repo.get_by_id.return_value = mock_seat
        self.service.reservation_repo.filter_by_flight_seat_status.return_value.exists.return_value = False
        self.service.reservation_repo.create.return_value = mock_reservation

        reservation = self.service.create_reservation(1, 1, 1, Decimal('100.00'))

        self.service.flight_repo.get_by_id.assert_called_once_with(1)
        self.service.passenger_repo.get_by_id.assert_called_once_with(1)
        self.service.seat_repo.get_by_id.assert_called_once_with(1)
        self.service.reservation_repo.filter_by_flight_seat_status.assert_called_once_with(mock_flight, mock_seat, ['PEN', 'CON', 'PAID'])
        self.service.reservation_repo.create.assert_called_once()
        self.service.seat_repo.update.assert_called_once_with(mock_seat.pk, {'status': 'Reserved'})
        self.assertEqual(reservation, mock_reservation)
        self.assertEqual(mock_seat.status, 'Reserved')

    @patch('airline.services.transaction.atomic')
    def test_create_reservation_seat_already_reserved(self, mock_atomic):
        mock_flight = MagicMock(spec=Flight)
        mock_passenger = MagicMock(spec=Passenger)
        mock_seat = MagicMock(spec=Seat)

        self.service.flight_repo.get_by_id.return_value = mock_flight
        self.service.passenger_repo.get_by_id.return_value = mock_passenger
        self.service.seat_repo.get_by_id.return_value = mock_seat
        self.service.reservation_repo.filter_by_flight_seat_status.return_value.exists.return_value = True

        with self.assertRaises(ValidationError):
            self.service.create_reservation(1, 1, 1, Decimal('100.00'))

        self.service.reservation_repo.create.assert_not_called()
        self.service.seat_repo.update.assert_not_called()

    def test_update_reservation(self):
        self.mock_repo.update.return_value = True
        data = {'status': 'CON'}
        result = self.service.update_reservation(1, data)
        self.mock_repo.update.assert_called_once_with(1, data)
        self.assertTrue(result)

    @patch('airline.services.transaction.atomic')
    def test_delete_reservation(self, mock_atomic):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.seat.pk = 1
        self.mock_repo.get_by_id.return_value = mock_reservation
        self.mock_repo.delete.return_value = True
        self.service.seat_repo.update.return_value = True

        result = self.service.delete_reservation(1)

        self.mock_repo.get_by_id.assert_called_once_with(1)
        self.mock_repo.delete.assert_called_once_with(1)
        self.service.seat_repo.update.assert_called_once_with(mock_reservation.seat.pk, {'status': 'Available'})
        self.assertTrue(result)

    def test_confirm_reservation_success(self):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.status = 'PEN'
        self.mock_repo.get_by_id.return_value = mock_reservation

        reservation = self.service.confirm_reservation(1)

        self.mock_repo.get_by_id.assert_called_once_with(1)
        self.assertEqual(reservation.status, 'CON')
        reservation.save.assert_called_once()

    def test_confirm_reservation_cancelled(self):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.status = 'CAN'
        self.mock_repo.get_by_id.return_value = mock_reservation

        with self.assertRaises(ValidationError):
            self.service.confirm_reservation(1)

        mock_reservation.save.assert_not_called()

    def test_cancel_reservation_success(self):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.status = 'PEN'
        self.mock_repo.get_by_id.return_value = mock_reservation

        reservation = self.service.cancel_reservation(1)

        self.mock_repo.get_by_id.assert_called_once_with(1)
        self.assertEqual(reservation.status, 'CAN')
        reservation.save.assert_called_once()

    def test_cancel_reservation_confirmed_or_paid(self):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.status = 'CON'
        self.mock_repo.get_by_id.return_value = mock_reservation

        with self.assertRaises(ValidationError):
            self.service.cancel_reservation(1)

        mock_reservation.status = 'PAID'
        with self.assertRaises(ValidationError):
            self.service.cancel_reservation(1)

        mock_reservation.save.assert_not_called()

    def test_get_reservations_list(self):
        mock_queryset = MagicMock()
        self.mock_repo.get_all.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset

        reservations = self.service.get_reservations_list()

        self.mock_repo.get_all.assert_called_once()
        mock_queryset.order_by.assert_called_once_with('-reservation_date')
        self.assertEqual(reservations, mock_queryset)

    def test_update_reservation_status(self):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.status = 'PEN'
        self.mock_repo.get_by_id.return_value = mock_reservation
        
        with patch('airline.models.Reservation.RESERVATION_STATUS_CHOICES', [('PEN', 'Pending'), ('CON', 'Confirmed')]):
            reservation = self.service.update_reservation_status(1, 'CON')

            self.mock_repo.get_by_id.assert_called_once_with(1)
            self.assertEqual(reservation.status, 'CON')
            reservation.save.assert_called_once()

    def test_get_flight_details_with_seats(self):
        mock_flight = MagicMock(spec=Flight)
        mock_flight.airplane = MagicMock(spec=Airplane)
        self.service.flight_repo.get_by_id.return_value = mock_flight

        mock_seat1 = MagicMock(spec=Seat, id=1, row=1, column='A')
        mock_seat2 = MagicMock(spec=Seat, id=2, row=1, column='B')
        mock_seat3 = MagicMock(spec=Seat, id=3, row=2, column='A')
        self.service.seat_repo.filter_by_airplane_ordered.return_value = [mock_seat1, mock_seat2, mock_seat3]

        self.service.reservation_repo.filter_by_flight_seat_status.return_value.values_list.return_value = [2]

        flight, seats_by_row = self.service.get_flight_details_with_seats(1)

        self.service.flight_repo.get_by_id.assert_called_once_with(1)
        self.service.seat_repo.filter_by_airplane_ordered.assert_called_once_with(mock_flight.airplane)
        self.service.reservation_repo.filter_by_flight_seat_status.assert_called_once_with(mock_flight, None, ['PEN', 'CON', 'PAID'])
        
        self.assertEqual(flight, mock_flight)
        self.assertTrue(mock_seat1.is_reserved == False)
        self.assertTrue(mock_seat2.is_reserved == True)
        self.assertTrue(mock_seat3.is_reserved == False)
        self.assertEqual(len(seats_by_row), 2)
        self.assertEqual(seats_by_row[1], [mock_seat1, mock_seat2])
        self.assertEqual(seats_by_row[2], [mock_seat3])

    def test_get_passengers_by_flight(self):
        mock_flight = MagicMock(spec=Flight)
        self.service.flight_repo.get_by_id.return_value = mock_flight

        mock_queryset = MagicMock()
        self.service.reservation_repo.filter_by_flight_and_select_related.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset

        flight, reservations = self.service.get_passengers_by_flight(1)

        self.service.flight_repo.get_by_id.assert_called_once_with(1)
        self.service.reservation_repo.filter_by_flight_and_select_related.assert_called_once_with(mock_flight)
        mock_queryset.order_by.assert_called_once_with('passenger__last_name', 'passenger__first_name')
        self.assertEqual(flight, mock_flight)
        self.assertEqual(reservations, mock_queryset)

class SeatLayoutServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = SeatLayoutService()
        self.service.seat_layout_repo = self.mock_repo
        self.service.seat_layout_position_repo = MagicMock()
        self.service.seat_type_repo = MagicMock()

    @patch('airline.services.transaction.atomic')
    def test_create_seat_layout_with_positions(self, mock_atomic):
        mock_seat_layout = MagicMock(spec=SeatLayout)
        self.mock_repo.create.return_value = mock_seat_layout
        mock_seat_type = MagicMock(spec=SeatType)
        self.service.seat_type_repo.get_by_id.return_value = mock_seat_type

        positions_data = [
            {'seat_type_id': 1, 'row': 1, 'column': 'A'},
            {'seat_type_id': 1, 'row': 1, 'column': 'B'}
        ]
        seat_layout = self.service.create_seat_layout_with_positions('Layout 1', 1, 2, positions_data)

        self.mock_repo.create.assert_called_once_with({
            'layout_name': 'Layout 1',
            'rows': 1,
            'columns': 2
        })
        self.assertEqual(self.service.seat_layout_position_repo.create.call_count, 2)
        self.assertEqual(seat_layout, mock_seat_layout)

    def test_update_seat_layout(self):
        self.mock_repo.update.return_value = True
        data = {'layout_name': 'Layout 2'}
        result = self.service.update_seat_layout(1, data)
        self.mock_repo.update.assert_called_once_with(1, data)
        self.assertTrue(result)

    def test_delete_seat_layout(self):
        self.mock_repo.delete.return_value = True
        result = self.service.delete_seat_layout(1)
        self.mock_repo.delete.assert_called_once_with(1)
        self.assertTrue(result)

class SeatTypeServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = SeatTypeService()
        self.service.seat_type_repo = self.mock_repo

    def test_create_seat_type(self):
        mock_seat_type = MagicMock(spec=SeatType)
        self.mock_repo.create.return_value = mock_seat_type
        data = {'name': 'Economy'}
        seat_type = self.service.create_seat_type(data)
        self.mock_repo.create.assert_called_once_with(data)
        self.assertEqual(seat_type, mock_seat_type)

    def test_update_seat_type(self):
        self.mock_repo.update.return_value = True
        data = {'name': 'Business'}
        result = self.service.update_seat_type(1, data)
        self.mock_repo.update.assert_called_once_with(1, data)
        self.assertTrue(result)

    def test_delete_seat_type(self):
        self.mock_repo.delete.return_value = True
        result = self.service.delete_seat_type(1)
        self.mock_repo.delete.assert_called_once_with(1)
        self.assertTrue(result)

class SeatLayoutPositionServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = SeatLayoutPositionService()
        self.service.seat_layout_position_repo = self.mock_repo

    def test_create_seat_layout_position(self):
        mock_position = MagicMock(spec=SeatLayoutPosition)
        self.mock_repo.create.return_value = mock_position
        data = {'row': 1, 'column': 'A'}
        position = self.service.create_seat_layout_position(data)
        self.mock_repo.create.assert_called_once_with(data)
        self.assertEqual(position, mock_position)

    def test_update_seat_layout_position(self):
        self.mock_repo.update.return_value = True
        data = {'row': 2}
        result = self.service.update_seat_layout_position(1, data)
        self.mock_repo.update.assert_called_once_with(1, data)
        self.assertTrue(result)

    def test_delete_seat_layout_position(self):
        self.mock_repo.delete.return_value = True
        result = self.service.delete_seat_layout_position(1)
        self.mock_repo.delete.assert_called_once_with(1)
        self.assertTrue(result)

class FlightHistoryServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = FlightHistoryService()
        self.service.flight_history_repo = self.mock_repo
        self.service.passenger_repo = MagicMock()
        self.service.flight_repo = MagicMock()

    def test_get_flight_history_by_passenger(self):
        mock_passenger = MagicMock(spec=Passenger)
        self.service.passenger_repo.get_by_id.return_value = mock_passenger
        mock_history = [MagicMock(spec=FlightHistory)]
        self.mock_repo.filter_by_passenger_ordered.return_value = mock_history

        history = self.service.get_flight_history_by_passenger(1)

        self.service.passenger_repo.get_by_id.assert_called_once_with(1)
        self.mock_repo.filter_by_passenger_ordered.assert_called_once_with(mock_passenger)
        self.assertEqual(history, mock_history)

    def test_get_flight_history_by_flight(self):
        mock_flight = MagicMock(spec=Flight, pk=1)
        self.service.flight_repo.get_by_id.return_value = mock_flight
        mock_history = [MagicMock(spec=FlightHistory)]
        self.mock_repo.filter_by_flight.return_value = mock_history

        history = self.service.get_flight_history_by_flight(1)

        self.service.flight_repo.get_by_id.assert_called_once_with(1)
        self.mock_repo.filter_by_flight.assert_called_once_with(mock_flight.pk)
        self.assertEqual(history, mock_history)

class TicketServiceTest(BaseServiceTest):
    def setUp(self):
        super().setUp()
        self.service = TicketService()
        self.service.ticket_repo = self.mock_repo
        self.service.reservation_repo = MagicMock()

    def test_issue_ticket_success(self):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.status = 'CON'
        self.service.reservation_repo.get_by_id.return_value = mock_reservation
        mock_ticket = MagicMock(spec=Ticket)
        self.mock_repo.get_or_create_ticket.return_value = (mock_ticket, True)

        ticket = self.service.issue_ticket(1)

        self.service.reservation_repo.get_by_id.assert_called_once_with(1)
        self.mock_repo.get_or_create_ticket.assert_called_once()
        self.assertEqual(ticket, mock_ticket)

    def test_issue_ticket_invalid_status(self):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.status = 'PEN'
        self.service.reservation_repo.get_by_id.return_value = mock_reservation

        with self.assertRaises(ValidationError):
            self.service.issue_ticket(1)

        self.mock_repo.get_or_create_ticket.assert_not_called()

    def test_cancel_ticket_success(self):
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.status = 'EMI'
        self.mock_repo.get_by_id.return_value = mock_ticket

        ticket = self.service.cancel_ticket(1)

        self.mock_repo.get_by_id.assert_called_once_with(1)
        self.assertEqual(ticket.status, 'CAN')
        ticket.save.assert_called_once()

    def test_cancel_ticket_used(self):
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.status = 'USED'
        self.mock_repo.get_by_id.return_value = mock_ticket

        with self.assertRaises(ValidationError):
            self.service.cancel_ticket(1)

        mock_ticket.save.assert_not_called()

    def test_delete_ticket(self):
        self.mock_repo.delete.return_value = True
        result = self.service.delete_ticket(1)
        self.mock_repo.delete.assert_called_once_with(1)
        self.assertTrue(result)

    def test_get_ticket_detail(self):
        mock_ticket = MagicMock(spec=Ticket)
        self.mock_repo.get_by_id.return_value = mock_ticket

        ticket = self.service.get_ticket_detail(1)

        self.mock_repo.get_by_id.assert_called_once_with(1)
        self.assertEqual(ticket, mock_ticket)
