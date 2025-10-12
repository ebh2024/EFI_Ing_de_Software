from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Flight, Passenger, Reservation, Seat, Ticket, SeatLayout, SeatLayoutPosition, SeatType, Airplane, FlightHistory
from .repositories import (
    FlightRepository, PassengerRepository, ReservationRepository,
    SeatRepository, TicketRepository, SeatLayoutRepository,
    SeatLayoutPositionRepository, SeatTypeRepository, AirplaneRepository,
    FlightHistoryRepository
)
import uuid
from datetime import datetime

class FlightService:
    def __init__(self):
        self.flight_repo = FlightRepository()
        self.airplane_repo = AirplaneRepository()
        self.seat_repo = SeatRepository()

    def create_flight(self, data):
        # Additional business logic for flight creation can go here
        # e.g., validate airplane capacity against seat layout
        return self.flight_repo.create(data)

    def get_flight(self, flight_id):
        return self.flight_repo.get_by_id(flight_id)

    def update_flight(self, flight_id, data):
        return self.flight_repo.update(flight_id, data)

    def delete_flight(self, flight_id):
        return self.flight_repo.delete(flight_id)

    def get_available_seats(self, flight_id):
        flight = self.flight_repo.get_by_id(flight_id)
        if not flight:
            raise ValidationError("Flight not found.")
        
        # Assuming Seat model has a foreign key to Airplane, and Airplane to SeatLayout
        # This logic might need to be refined based on how seats are truly managed per flight
        # For now, we'll assume seats are associated with the airplane, and their status
        # is managed through reservations.
        all_seats = self.seat_repo.filter(airplane=flight.airplane)
        reserved_seat_ids = Reservation.objects.filter(
            flight=flight,
            status__in=['PEN', 'CON', 'PAID']
        ).values_list('seat__id', flat=True)
        
        available_seats = [seat for seat in all_seats if seat.id not in reserved_seat_ids]
        return available_seats

class PassengerService:
    def __init__(self):
        self.passenger_repo = PassengerRepository()

    def create_passenger(self, data):
        return self.passenger_repo.create(data)

    def get_passenger(self, passenger_id):
        return self.passenger_repo.get_by_id(passenger_id)

    def update_passenger(self, passenger_id, data):
        return self.passenger_repo.update(passenger_id, data)

    def delete_passenger(self, passenger_id):
        return self.passenger_repo.delete(passenger_id)

class ReservationService:
    def __init__(self):
        self.reservation_repo = ReservationRepository()
        self.flight_repo = FlightRepository()
        self.passenger_repo = PassengerRepository()
        self.seat_repo = SeatRepository()
        self.ticket_repo = TicketRepository()
        self.flight_history_repo = FlightHistoryRepository()

    @transaction.atomic
    def create_reservation(self, flight_id, passenger_id, seat_id, price):
        flight = self.flight_repo.get_by_id(flight_id)
        passenger = self.passenger_repo.get_by_id(passenger_id)
        seat = self.seat_repo.get_by_id(seat_id)

        if not all([flight, passenger, seat]):
            raise ValidationError("Flight, passenger, or seat not found.")

        if Reservation.objects.filter(flight=flight, seat=seat, status__in=['PEN', 'CON', 'PAID']).exists():
            raise ValidationError("This seat is already reserved for this flight.")
        
        if Reservation.objects.filter(flight=flight, passenger=passenger, status__in=['PEN', 'CON', 'PAID']).exists():
            raise ValidationError("This passenger already has a reservation for this flight.")

        reservation_code = str(uuid.uuid4())[:20] # Generate a unique reservation code
        reservation_data = {
            'flight': flight,
            'passenger': passenger,
            'seat': seat,
            'status': 'PEN',
            'price': price,
            'reservation_code': reservation_code
        }
        reservation = self.reservation_repo.create(reservation_data)

        # Update seat status
        seat.status = 'Reserved'
        self.seat_repo.update(seat.id, {'status': 'Reserved'})

        # Create flight history entry
        flight_history_data = {
            'passenger': passenger,
            'flight': flight,
            'seat_number': seat.number,
            'price_paid': price,
            'booking_date': datetime.now()
        }
        self.flight_history_repo.create(flight_history_data)

        return reservation

    @transaction.atomic
    def confirm_reservation(self, reservation_id):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValidationError("Reservation not found.")
        
        if reservation.status == 'CON':
            raise ValidationError("Reservation is already confirmed.")

        reservation = self.reservation_repo.update(reservation_id, {'status': 'CON'})
        # The save method of Reservation model handles seat status update
        return reservation

    @transaction.atomic
    def cancel_reservation(self, reservation_id):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValidationError("Reservation not found.")
        
        if reservation.status == 'CAN':
            raise ValidationError("Reservation is already cancelled.")

        reservation = self.reservation_repo.update(reservation_id, {'status': 'CAN'})
        # The save method of Reservation model handles seat status update
        
        # Also cancel any associated ticket
        ticket = self.ticket_repo.filter(reservation=reservation).first()
        if ticket:
            self.ticket_repo.update(ticket.id, {'status': 'CAN'})

        return reservation

    def get_reservation(self, reservation_id):
        return self.reservation_repo.get_by_id(reservation_id)

    def get_reservations_by_passenger(self, passenger_id):
        passenger = self.passenger_repo.get_by_id(passenger_id)
        if not passenger:
            raise ValidationError("Passenger not found.")
        return self.reservation_repo.filter(passenger=passenger)

class TicketService:
    def __init__(self):
        self.ticket_repo = TicketRepository()
        self.reservation_repo = ReservationRepository()

    @transaction.atomic
    def issue_ticket(self, reservation_id):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValidationError("Reservation not found.")
        
        if reservation.status != 'CON' and reservation.status != 'PAID':
            raise ValidationError("Reservation must be confirmed or paid to issue a ticket.")
        
        if self.ticket_repo.filter(reservation=reservation).exists():
            raise ValidationError("Ticket already issued for this reservation.")

        barcode = str(uuid.uuid4())[:50] # Generate a unique barcode
        ticket_data = {
            'reservation': reservation,
            'barcode': barcode,
            'status': 'EMI'
        }
        ticket = self.ticket_repo.create(ticket_data)
        return ticket

    def get_ticket(self, ticket_id):
        return self.ticket_repo.get_by_id(ticket_id)

    def cancel_ticket(self, ticket_id):
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValidationError("Ticket not found.")
        
        if ticket.status == 'CAN':
            raise ValidationError("Ticket is already cancelled.")
        
        return self.ticket_repo.update(ticket_id, {'status': 'CAN'})

class SeatLayoutService:
    def __init__(self):
        self.seat_layout_repo = SeatLayoutRepository()
        self.seat_layout_position_repo = SeatLayoutPositionRepository()
        self.seat_type_repo = SeatTypeRepository()

    @transaction.atomic
    def create_seat_layout_with_positions(self, layout_name, rows, columns, positions_data):
        seat_layout = self.seat_layout_repo.create({
            'layout_name': layout_name,
            'rows': rows,
            'columns': columns
        })

        for pos_data in positions_data:
            seat_type = self.seat_type_repo.get_by_id(pos_data['seat_type_id'])
            if not seat_type:
                raise ValidationError(f"Seat type with ID {pos_data['seat_type_id']} not found.")
            
            self.seat_layout_position_repo.create({
                'seat_layout': seat_layout,
                'seat_type': seat_type,
                'row': pos_data['row'],
                'column': pos_data['column']
            })
        return seat_layout

    def get_seat_layout(self, layout_id):
        return self.seat_layout_repo.get_by_id(layout_id)

    def update_seat_layout(self, layout_id, data):
        return self.seat_layout_repo.update(layout_id, data)

    def delete_seat_layout(self, layout_id):
        return self.seat_layout_repo.delete(layout_id)

class SeatTypeService:
    def __init__(self):
        self.seat_type_repo = SeatTypeRepository()

    def create_seat_type(self, data):
        return self.seat_type_repo.create(data)

    def get_seat_type(self, seat_type_id):
        return self.seat_type_repo.get_by_id(seat_type_id)

    def update_seat_type(self, seat_type_id, data):
        return self.seat_type_repo.update(seat_type_id, data)

    def delete_seat_type(self, seat_type_id):
        return self.seat_type_repo.delete(seat_type_id)

class AirplaneService:
    def __init__(self):
        self.airplane_repo = AirplaneRepository()
        self.seat_layout_repo = SeatLayoutRepository()
        self.seat_repo = SeatRepository()

    @transaction.atomic
    def create_airplane_with_seats(self, data):
        seat_layout_id = data.pop('seat_layout_id', None)
        seat_layout = None
        if seat_layout_id:
            seat_layout = self.seat_layout_repo.get_by_id(seat_layout_id)
            if not seat_layout:
                raise ValidationError(f"Seat layout with ID {seat_layout_id} not found.")
            data['seat_layout'] = seat_layout

        airplane = self.airplane_repo.create(data)

        if seat_layout:
            # Generate seats based on the seat layout
            for position in seat_layout.positions.all():
                seat_number = f"{position.row}{position.column}"
                self.seat_repo.create({
                    'airplane': airplane,
                    'number': seat_number,
                    'row': position.row,
                    'column': position.column,
                    'seat_type': position.seat_type,
                    'status': 'Available'
                })
        return airplane

    def get_airplane(self, airplane_id):
        return self.airplane_repo.get_by_id(airplane_id)

    def update_airplane(self, airplane_id, data):
        seat_layout_id = data.pop('seat_layout_id', None)
        if seat_layout_id:
            seat_layout = self.seat_layout_repo.get_by_id(seat_layout_id)
            if not seat_layout:
                raise ValidationError(f"Seat layout with ID {seat_layout_id} not found.")
            data['seat_layout'] = seat_layout
        return self.airplane_repo.update(airplane_id, data)

    def delete_airplane(self, airplane_id):
        return self.airplane_repo.delete(airplane_id)

class FlightHistoryService:
    def __init__(self):
        self.flight_history_repo = FlightHistoryRepository()

    def get_flight_history_by_passenger(self, passenger_id):
        return self.flight_history_repo.filter(passenger__id=passenger_id)

    def get_flight_history_by_flight(self, flight_id):
        return self.flight_history_repo.filter(flight__id=flight_id)
