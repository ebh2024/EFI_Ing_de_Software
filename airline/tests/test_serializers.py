from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from airline.models import (
    Airplane, Flight, Passenger, Reservation, SeatLayout, SeatType,
    SeatLayoutPosition, FlightHistory, Ticket, Seat
)
from airline.serializers import (
    SeatTypeSerializer, SeatLayoutPositionSerializer, SeatLayoutSerializer,
    AirplaneSerializer, FlightSerializer, PassengerSerializer,
    SeatSerializer, ReservationSerializer, FlightHistorySerializer,
    TicketSerializer
)

class SeatTypeSerializerTest(TestCase):
    def setUp(self):
        self.seat_type_data = {'name': 'Economy', 'code': 'ECO', 'price_multiplier': Decimal('1.00')}
        self.seat_type = SeatType.objects.create(**self.seat_type_data)
        self.serializer = SeatTypeSerializer(instance=self.seat_type)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'name', 'code', 'price_multiplier'])

    def test_name_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['name'], self.seat_type_data['name'])

    def test_price_multiplier_field_content(self):
        data = self.serializer.data
        self.assertEqual(Decimal(data['price_multiplier']), self.seat_type_data['price_multiplier'])

    def test_create_seat_type(self):
        new_seat_type_data = {'name': 'Business', 'code': 'BUS', 'price_multiplier': Decimal('1.50')}
        serializer = SeatTypeSerializer(data=new_seat_type_data)
        self.assertTrue(serializer.is_valid())
        seat_type = serializer.save()
        self.assertEqual(seat_type.name, new_seat_type_data['name'])
        self.assertEqual(seat_type.price_multiplier, new_seat_type_data['price_multiplier'])

    def test_update_seat_type(self):
        updated_data = {'name': 'Premium Economy', 'price_multiplier': Decimal('1.20')}
        serializer = SeatTypeSerializer(instance=self.seat_type, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        seat_type = serializer.save()
        self.assertEqual(seat_type.name, updated_data['name'])
        self.assertEqual(seat_type.price_multiplier, updated_data['price_multiplier'])

class SeatLayoutPositionSerializerTest(TestCase):
    def setUp(self):
        self.seat_type = SeatType.objects.create(name='Economy', code='ECO', price_multiplier=Decimal('1.00'))
        self.seat_layout = SeatLayout.objects.create(layout_name='Layout A', rows=10, columns=6)
        self.seat_layout_position_data = {
            'seat_layout': self.seat_layout,
            'row': 1,
            'column': 'A',
            'seat_type': self.seat_type
        }
        self.seat_layout_position = SeatLayoutPosition.objects.create(**self.seat_layout_position_data)
        self.serializer = SeatLayoutPositionSerializer(instance=self.seat_layout_position)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'seat_layout', 'row', 'column', 'seat_type', 'seat_number'])

    def test_seat_layout_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['seat_layout'], self.seat_layout.id)

    def test_seat_type_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['seat_type'], self.seat_type.id)

    def test_seat_number_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['seat_number'], self.seat_layout_position.seat_number)

    def test_create_seat_layout_position(self):
        new_seat_type = SeatType.objects.create(name='Business', code='BUS', price_multiplier=Decimal('1.50'))
        new_seat_layout_position_data = {
            'seat_layout': self.seat_layout.id,
            'row': 2,
            'column': 'B',
            'seat_type': new_seat_type.id
        }
        serializer = SeatLayoutPositionSerializer(data=new_seat_layout_position_data)
        self.assertTrue(serializer.is_valid())
        seat_layout_position = serializer.save()
        self.assertEqual(seat_layout_position.row, new_seat_layout_position_data['row'])
        self.assertEqual(seat_layout_position.column, new_seat_layout_position_data['column'])
        self.assertEqual(seat_layout_position.seat_type, new_seat_type)

    def test_update_seat_layout_position(self):
        updated_seat_type = SeatType.objects.create(name='First Class', code='FST', price_multiplier=Decimal('2.00'))
        updated_data = {'seat_type': updated_seat_type.id}
        serializer = SeatLayoutPositionSerializer(instance=self.seat_layout_position, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        seat_layout_position = serializer.save()
        self.assertEqual(seat_layout_position.seat_type, updated_seat_type)

class SeatLayoutSerializerTest(TestCase):
    def setUp(self):
        self.seat_layout_data = {'layout_name': 'Layout B', 'rows': 15, 'columns': 4}
        self.seat_layout = SeatLayout.objects.create(**self.seat_layout_data)
        self.seat_type = SeatType.objects.create(name='Economy', code='ECO', price_multiplier=Decimal('1.00'))
        SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout, row=1, column='A', seat_type=self.seat_type
        )
        self.serializer = SeatLayoutSerializer(instance=self.seat_layout)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'layout_name', 'rows', 'columns', 'positions'])

    def test_name_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['layout_name'], self.seat_layout_data['layout_name'])

    def test_positions_field_content(self):
        data = self.serializer.data
        self.assertEqual(len(data['positions']), 1)
        self.assertEqual(data['positions'][0]['row'], 1) # Changed from row_number to row

    def test_create_seat_layout(self):
        new_seat_layout_data = {'layout_name': 'Layout C', 'rows': 20, 'columns': 8}
        serializer = SeatLayoutSerializer(data=new_seat_layout_data)
        self.assertTrue(serializer.is_valid())
        seat_layout = serializer.save()
        self.assertEqual(seat_layout.layout_name, new_seat_layout_data['layout_name'])

    def test_update_seat_layout(self):
        updated_data = {'layout_name': 'Layout D', 'rows': 18}
        serializer = SeatLayoutSerializer(instance=self.seat_layout, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        seat_layout = serializer.save()
        self.assertEqual(seat_layout.layout_name, updated_data['layout_name'])
        self.assertEqual(seat_layout.rows, updated_data['rows'])

class AirplaneSerializerTest(TestCase):
    def setUp(self):
        self.seat_layout = SeatLayout.objects.create(layout_name='Layout A', rows=10, columns=6)
        self.airplane_data = {
            'registration_number': 'N12345',
            'model_name': 'Boeing 737',
            'manufacturer': 'Boeing',
            'year_of_manufacture': 2020,
            'capacity': 150,
            'seat_layout': self.seat_layout,
            'last_maintenance_date': '2024-01-01',
            'technical_notes': 'Some notes'
        }
        self.airplane = Airplane.objects.create(**self.airplane_data)
        self.serializer = AirplaneSerializer(instance=self.airplane)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'registration_number', 'model_name', 'manufacturer', 'year_of_manufacture', 'capacity', 'seat_layout', 'last_maintenance_date', 'technical_notes'])

    def test_registration_number_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['registration_number'], self.airplane_data['registration_number'])

    def test_seat_layout_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['seat_layout'], self.seat_layout.id)

    def test_create_airplane(self):
        new_seat_layout = SeatLayout.objects.create(layout_name='Layout B', rows=12, columns=8)
        new_airplane_data = {
            'registration_number': 'N54321',
            'model_name': 'Airbus A320',
            'manufacturer': 'Airbus',
            'year_of_manufacture': 2021,
            'capacity': 180,
            'seat_layout': new_seat_layout.id,
            'last_maintenance_date': '2024-02-01',
            'technical_notes': 'Other notes'
        }
        serializer = AirplaneSerializer(data=new_airplane_data)
        self.assertTrue(serializer.is_valid())
        airplane = serializer.save()
        self.assertEqual(airplane.registration_number, new_airplane_data['registration_number'])
        self.assertEqual(airplane.seat_layout, new_seat_layout)

    def test_update_airplane(self):
        updated_seat_layout = SeatLayout.objects.create(layout_name='Layout C', rows=10, columns=5)
        updated_data = {'model_name': 'Boeing 747', 'seat_layout': updated_seat_layout.id}
        serializer = AirplaneSerializer(instance=self.airplane, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        airplane = serializer.save()
        self.assertEqual(airplane.model_name, updated_data['model_name'])
        self.assertEqual(airplane.seat_layout, updated_seat_layout)

class FlightSerializerTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(registration_number='N12345', model_name='Boeing 737', capacity=150)
        self.flight_data = {
            'origin': 'JFK',
            'destination': 'LAX',
            'departure_date': '2025-10-26T10:00:00Z',
            'arrival_date': '2025-10-26T13:00:00Z',
            'duration': timedelta(hours=3),
            'status': 'Scheduled',
            'base_price': Decimal('200.00'),
            'airplane': self.airplane
        }
        self.flight = Flight.objects.create(**self.flight_data)
        self.serializer = FlightSerializer(instance=self.flight)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'origin', 'destination', 'departure_date', 'arrival_date', 'duration', 'status', 'base_price', 'airplane'])

    def test_flight_number_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['origin'], self.flight_data['origin']) # Changed to origin

    def test_airplane_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['airplane'], self.airplane.id)

    def test_create_flight(self):
        new_airplane = Airplane.objects.create(registration_number='N54321', model_name='Airbus A320', capacity=180)
        new_flight_data = {
            'origin': 'LAX',
            'destination': 'JFK',
            'departure_date': '2025-10-27T10:00:00Z',
            'arrival_date': '2025-10-27T13:00:00Z',
            'duration': timedelta(hours=3),
            'status': 'Scheduled',
            'base_price': Decimal('250.00'),
            'airplane': new_airplane.id
        }
        serializer = FlightSerializer(data=new_flight_data)
        self.assertTrue(serializer.is_valid())
        flight = serializer.save()
        self.assertEqual(flight.origin, new_flight_data['origin']) # Changed to origin
        self.assertEqual(flight.airplane, new_airplane)

    def test_update_flight(self):
        updated_airplane = Airplane.objects.create(registration_number='N98765', model_name='Boeing 747', capacity=300)
        updated_data = {'destination': 'ORD', 'airplane': updated_airplane.id}
        serializer = FlightSerializer(instance=self.flight, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        flight = serializer.save()
        self.assertEqual(flight.destination, updated_data['destination'])
        self.assertEqual(flight.airplane, updated_airplane)

class PassengerSerializerTest(TestCase):
    def setUp(self):
        self.passenger_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'document_number': '12345678',
            'email': 'john.doe@example.com',
            'phone': '123-456-7890',
            'date_of_birth': '1990-01-01',
            'document_type': 'DNI'
        }
        self.passenger = Passenger.objects.create(**self.passenger_data)
        self.serializer = PassengerSerializer(instance=self.passenger)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'first_name', 'last_name', 'document_number', 'email', 'phone', 'date_of_birth', 'document_type'])

    def test_first_name_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['first_name'], self.passenger_data['first_name'])

    def test_create_passenger(self):
        new_passenger_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'document_number': '87654321',
            'email': 'jane.smith@example.com',
            'phone': '098-765-4321',
            'date_of_birth': '1992-02-02',
            'document_type': 'PAS'
        }
        serializer = PassengerSerializer(data=new_passenger_data)
        self.assertTrue(serializer.is_valid())
        passenger = serializer.save()
        self.assertEqual(passenger.first_name, new_passenger_data['first_name'])
        self.assertEqual(passenger.email, new_passenger_data['email'])

    def test_update_passenger(self):
        updated_data = {'email': 'john.new.email@example.com'}
        serializer = PassengerSerializer(instance=self.passenger, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        passenger = serializer.save()
        self.assertEqual(passenger.email, updated_data['email'])

class SeatSerializerTest(TestCase):
    def setUp(self):
        self.seat_type = SeatType.objects.create(name='Economy', code='ECO', price_multiplier=Decimal('1.00'))
        self.seat_layout = SeatLayout.objects.create(layout_name='Layout A', rows=10, columns=6)
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout, row=1, column='A', seat_type=self.seat_type
        )
        self.airplane = Airplane.objects.create(registration_number='N12345', model_name='Boeing 737', capacity=150, seat_layout=self.seat_layout)
        self.seat_data = {
            'airplane': self.airplane,
            'number': '1A',
            'row': 1,
            'column': 'A',
            'seat_type': self.seat_type,
            'status': 'Available'
        }
        self.seat = Seat.objects.create(**self.seat_data)
        self.serializer = SeatSerializer(instance=self.seat)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'airplane', 'number', 'row', 'column', 'seat_type', 'status'])

    def test_is_available_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['status'], self.seat_data['status'])

    def test_seat_type_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['seat_type'], self.seat_type.id) # Changed to id as it's PrimaryKeyRelatedField

    def test_create_seat(self):
        new_seat_type = SeatType.objects.create(name='Business', code='BUS', price_multiplier=Decimal('1.50'))
        new_seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout, row=1, column='B', seat_type=new_seat_type
        )
        new_seat_data = {
            'airplane': self.airplane.id,
            'number': '1B',
            'row': 1,
            'column': 'B',
            'seat_type': new_seat_type.id,
            'status': 'Occupied'
        }
        serializer = SeatSerializer(data=new_seat_data)
        self.assertTrue(serializer.is_valid())
        seat = serializer.save()
        self.assertEqual(seat.status, new_seat_data['status'])
        self.assertEqual(seat.seat_type, new_seat_type)

    def test_update_seat(self):
        updated_data = {'status': 'Reserved'}
        serializer = SeatSerializer(instance=self.seat, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        seat = serializer.save()
        self.assertEqual(seat.status, updated_data['status'])

class ReservationSerializerTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(registration_number='N12345', model_name='Boeing 737', capacity=150)
        self.flight = Flight.objects.create(
            origin='JFK', destination='LAX',
            departure_date='2025-10-26T10:00:00Z', arrival_date='2025-10-26T13:00:00Z',
            duration=timedelta(hours=3), status='Scheduled', base_price=Decimal('200.00'),
            airplane=self.airplane
        )
        self.passenger = Passenger.objects.create(
            first_name='John', last_name='Doe', document_number='12345678',
            email='john.doe@example.com', phone='123-456-7890', date_of_birth='1990-01-01',
            document_type='DNI'
        )
        self.seat_type = SeatType.objects.create(name='Economy', code='ECO', price_multiplier=Decimal('1.00'))
        self.seat_layout = SeatLayout.objects.create(layout_name='Layout A', rows=10, columns=6)
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout, row=1, column='A', seat_type=self.seat_type
        )
        self.seat = Seat.objects.create(
            airplane=self.airplane, number='1A', row=1, column='A', seat_type=self.seat_type, status='Available'
        )
        self.reservation_data = {
            'flight': self.flight,
            'passenger': self.passenger,
            'seat': self.seat,
            'status': 'CON',
            'price': Decimal('250.00'),
            'reservation_code': 'RES12345'
        }
        self.reservation = Reservation.objects.create(**self.reservation_data)
        self.serializer = ReservationSerializer(instance=self.reservation)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'flight', 'passenger', 'seat', 'status', 'reservation_date', 'price', 'reservation_code'])

    def test_status_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['status'], self.reservation_data['status'])

    def test_create_reservation(self):
        new_flight = Flight.objects.create(
            origin='LAX', destination='JFK',
            departure_date='2025-10-27T10:00:00Z', arrival_date='2025-10-27T13:00:00Z',
            duration=timedelta(hours=3), status='Scheduled', base_price=Decimal('250.00'),
            airplane=self.airplane
        )
        new_passenger = Passenger.objects.create(
            first_name='Jane', last_name='Smith', document_number='87654321',
            email='jane.smith@example.com', phone='098-765-4321', date_of_birth='1992-02-02',
            document_type='PAS'
        )
        new_seat = Seat.objects.create(
            airplane=self.airplane, number='1B', row=1, column='B', seat_type=self.seat_type, status='Available'
        )
        new_reservation_data = {
            'flight': new_flight.id,
            'passenger': new_passenger.id,
            'seat': new_seat.id,
            'status': 'PEN',
            'price': Decimal('300.00'),
            'reservation_code': 'RES54321'
        }
        serializer = ReservationSerializer(data=new_reservation_data)
        self.assertTrue(serializer.is_valid())
        reservation = serializer.save()
        self.assertEqual(reservation.status, new_reservation_data['status'])
        self.assertEqual(reservation.flight, new_flight)

    def test_update_reservation(self):
        updated_data = {'status': 'CAN'}
        serializer = ReservationSerializer(instance=self.reservation, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        reservation = serializer.save()
        self.assertEqual(reservation.status, updated_data['status'])

class FlightHistorySerializerTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(registration_number='N12345', model_name='Boeing 737', capacity=150)
        self.flight = Flight.objects.create(
            origin='JFK', destination='LAX',
            departure_date='2025-10-26T10:00:00Z', arrival_date='2025-10-26T13:00:00Z',
            duration=timedelta(hours=3), status='Scheduled', base_price=Decimal('200.00'),
            airplane=self.airplane
        )
        self.passenger = Passenger.objects.create(
            first_name='John', last_name='Doe', document_number='12345678',
            email='john.doe@example.com', phone='123-456-7890', date_of_birth='1990-01-01',
            document_type='DNI'
        )
        self.flight_history_data = {
            'passenger': self.passenger,
            'flight': self.flight,
            'seat_number': '1A',
            'price_paid': Decimal('250.00')
        }
        self.flight_history = FlightHistory.objects.create(**self.flight_history_data)
        self.serializer = FlightHistorySerializer(instance=self.flight_history)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'passenger', 'flight', 'booking_date', 'seat_number', 'price_paid'])

    def test_seat_number_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['seat_number'], self.flight_history_data['seat_number'])

    def test_create_flight_history(self):
        new_passenger = Passenger.objects.create(
            first_name='Jane', last_name='Smith', document_number='87654321',
            email='jane.smith@example.com', phone='098-765-4321', date_of_birth='1992-02-02',
            document_type='PAS'
        )
        new_flight = Flight.objects.create(
            origin='LAX', destination='JFK',
            departure_date='2025-10-27T10:00:00Z', arrival_date='2025-10-27T13:00:00Z',
            duration=timedelta(hours=3), status='Scheduled', base_price=Decimal('250.00'),
            airplane=self.airplane
        )
        new_flight_history_data = {
            'passenger': new_passenger.id,
            'flight': new_flight.id,
            'seat_number': '2B',
            'price_paid': Decimal('300.00')
        }
        serializer = FlightHistorySerializer(data=new_flight_history_data)
        self.assertTrue(serializer.is_valid())
        flight_history = serializer.save()
        self.assertEqual(flight_history.seat_number, new_flight_history_data['seat_number'])
        self.assertEqual(flight_history.passenger, new_passenger)

    def test_update_flight_history(self):
        updated_data = {'price_paid': Decimal('275.00')}
        serializer = FlightHistorySerializer(instance=self.flight_history, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        flight_history = serializer.save()
        self.assertEqual(flight_history.price_paid, updated_data['price_paid'])

class TicketSerializerTest(TestCase):
    def setUp(self):
        self.airplane = Airplane.objects.create(registration_number='N12345', model_name='Boeing 737', capacity=150)
        self.flight = Flight.objects.create(
            origin='JFK', destination='LAX',
            departure_date='2025-10-26T10:00:00Z', arrival_date='2025-10-26T13:00:00Z',
            duration=timedelta(hours=3), status='Scheduled', base_price=Decimal('200.00'),
            airplane=self.airplane
        )
        self.passenger = Passenger.objects.create(
            first_name='John', last_name='Doe', document_number='12345678',
            email='john.doe@example.com', phone='123-456-7890', date_of_birth='1990-01-01',
            document_type='DNI'
        )
        self.seat_type = SeatType.objects.create(name='Economy', code='ECO', price_multiplier=Decimal('1.00'))
        self.seat_layout = SeatLayout.objects.create(layout_name='Layout A', rows=10, columns=6)
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout, row=1, column='A', seat_type=self.seat_type
        )
        self.seat = Seat.objects.create(
            airplane=self.airplane, number='1A', row=1, column='A', seat_type=self.seat_type, status='Available'
        )
        self.reservation = Reservation.objects.create(
            flight=self.flight, passenger=self.passenger, seat=self.seat,
            status='CON', price=Decimal('250.00'), reservation_code='RES12345'
        )
        self.ticket_data = {
            'reservation': self.reservation,
            'barcode': 'TKT12345',
            'status': 'EMI'
        }
        self.ticket = Ticket.objects.create(**self.ticket_data)
        self.serializer = TicketSerializer(instance=self.ticket)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'reservation', 'ticket_number', 'issue_date', 'status', 'barcode'])

    def test_ticket_number_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['ticket_number'], self.ticket_data['barcode'])

    def test_reservation_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['reservation'], self.reservation.id)

    def test_create_ticket(self):
        new_flight = Flight.objects.create(
            origin='LAX', destination='JFK',
            departure_date='2025-10-27T10:00:00Z', arrival_date='2025-10-27T13:00:00Z',
            duration=timedelta(hours=3), status='Scheduled', base_price=Decimal('250.00'),
            airplane=self.airplane
        )
        new_passenger = Passenger.objects.create(
            first_name='Jane', last_name='Smith', document_number='87654321',
            email='jane.smith@example.com', phone='098-765-4321', date_of_birth='1992-02-02',
            document_type='PAS'
        )
        new_seat = Seat.objects.create(
            airplane=self.airplane, number='1B', row=1, column='B', seat_type=self.seat_type, status='Available'
        )
        new_reservation = Reservation.objects.create(
            flight=new_flight, passenger=new_passenger, seat=new_seat,
            status='CON', price=Decimal('300.00'), reservation_code='RES54321'
        )
        new_ticket_data = {
            'reservation': new_reservation.id,
            'barcode': 'TKT54321',
            'status': 'EMI'
        }
        serializer = TicketSerializer(data=new_ticket_data)
        self.assertTrue(serializer.is_valid())
        ticket = serializer.save()
        self.assertEqual(ticket.ticket_number, new_ticket_data['barcode'])
        self.assertEqual(ticket.reservation, new_reservation)

    def test_update_ticket(self):
        updated_data = {'status': 'USED'}
        serializer = TicketSerializer(instance=self.ticket, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        ticket = serializer.save()
        self.assertEqual(ticket.status, updated_data['status'])
