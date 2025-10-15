from django.db import transaction
import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Airplane, Flight, Passenger, Seat, Reservation, Ticket, FlightHistory, SeatLayout, SeatType, SeatLayoutPosition
from .repositories import (
    AirplaneRepository, FlightRepository, PassengerRepository, SeatRepository, ReservationRepository,
    TicketRepository, FlightHistoryRepository, SeatLayoutRepository, SeatTypeRepository, SeatLayoutPositionRepository
)

class AirplaneService:
    def __init__(self):
        self.airplane_repo = AirplaneRepository()
        self.seat_layout_repo = SeatLayoutRepository()
        self.seat_repo = SeatRepository()

    def create_airplane_with_seats(self, data):
        seat_layout_id = data.pop('seat_layout', None)
        seat_layout = None
        if seat_layout_id:
            seat_layout = self.seat_layout_repo.get_by_id(seat_layout_id)
            data['seat_layout'] = seat_layout
        
        airplane = self.airplane_repo.create(data)

        if seat_layout:
            for row_num in range(1, seat_layout.rows + 1):
                for col_char_code in range(ord('A'), ord('A') + seat_layout.columns):
                    column = chr(col_char_code)
                    seat_number = f"{row_num}{column}"
                    # Find seat type from layout positions
                    seat_layout_position = SeatLayoutPosition.objects.filter(
                        seat_layout=seat_layout, row=row_num, column=column
                    ).first()
                    seat_type = seat_layout_position.seat_type if seat_layout_position else None

                    self.seat_repo.create({
                        'airplane': airplane,
                        'number': seat_number,
                        'row': row_num,
                        'column': column,
                        'seat_type': seat_type,
                        'status': 'Available'
                    })
        return airplane

    def update_airplane(self, pk, data):
        seat_layout_id = data.pop('seat_layout', None)
        seat_layout = None
        if seat_layout_id:
            seat_layout = self.seat_layout_repo.get_by_id(seat_layout_id)
            data['seat_layout'] = seat_layout
        return self.airplane_repo.update(pk, data)

    def delete_airplane(self, pk):
        return self.airplane_repo.delete(pk)

class FlightService:
    def __init__(self):
        self.flight_repo = FlightRepository()
        self.seat_repo = SeatRepository()
        self.reservation_repo = ReservationRepository()

    def create_flight(self, data):
        return self.flight_repo.create(data)

    def update_flight(self, pk, data):
        return self.flight_repo.update(pk, data)

    def delete_flight(self, pk):
        return self.flight_repo.delete(pk)

    def get_available_seats(self, flight_pk):
        flight = self.flight_repo.get_by_id(flight_pk)
        all_seats = self.seat_repo.filter_by_airplane_ordered(flight.airplane)
        reserved_seats_ids = self.reservation_repo.filter_by_flight_seat_status(flight, None, ['PEN', 'CON', 'PAID']).values_list('seat__id', flat=True)
        
        available_seats = [seat for seat in all_seats if seat.id not in reserved_seats_ids]
        return available_seats

class PassengerService:
    def __init__(self):
        self.passenger_repo = PassengerRepository()
        self.flight_history_repo = FlightHistoryRepository()

    def create_passenger(self, data):
        return self.passenger_repo.create(data)

    def update_passenger(self, pk, data):
        return self.passenger_repo.update(pk, data)

    def delete_passenger(self, pk):
        return self.passenger_repo.delete(pk)

    def get_or_create_passenger_for_user(self, user):
        passenger, created = self.passenger_repo.get_or_create_passenger(
            email=user.email,
            defaults={
                'first_name': user.first_name if user.first_name else user.username,
                'last_name': user.last_name if user.last_name else '',
                'document_number': str(uuid.uuid4())[:10],
                'date_of_birth': '2000-01-01'
            }
        )
        return passenger

    def get_passenger_flight_history(self, passenger_pk):
        passenger = self.passenger_repo.get_by_id(passenger_pk)
        flight_history = self.flight_history_repo.filter_by_passenger_ordered(passenger)
        return passenger, flight_history

class ReservationService:
    def __init__(self):
        self.reservation_repo = ReservationRepository()
        self.flight_repo = FlightRepository()
        self.passenger_repo = PassengerRepository()
        self.seat_repo = SeatRepository()

    def create_reservation(self, flight_id, passenger_id, seat_id, price):
        flight = self.flight_repo.get_by_id(flight_id)
        passenger = self.passenger_repo.get_by_id(passenger_id)
        seat = self.seat_repo.get_by_id(seat_id)

        if self.reservation_repo.filter_by_flight_seat_status(flight, seat, ['PEN', 'CON', 'PAID']).exists():
            raise ValidationError('This seat is already reserved for this flight.')

        with transaction.atomic():
            reservation = self.reservation_repo.create({
                'flight': flight,
                'passenger': passenger,
                'seat': seat,
                'status': 'PEN',
                'price': price,
                'reservation_code': str(uuid.uuid4()).replace('-', '')[:20]
            })
            seat.status = 'Reserved'
            self.seat_repo.update(seat.pk, {'status': 'Reserved'})
            return reservation

    def update_reservation(self, pk, data):
        return self.reservation_repo.update(pk, data)

    def delete_reservation(self, pk):
        reservation = self.reservation_repo.get_by_id(pk)
        with transaction.atomic():
            self.reservation_repo.delete(pk)
            self.seat_repo.update(reservation.seat.pk, {'status': 'Available'})
        return True

    def confirm_reservation(self, pk):
        reservation = self.reservation_repo.get_by_id(pk)
        if reservation.status == 'CAN':
            raise ValidationError('Cannot confirm a cancelled reservation.')
        reservation.status = 'CON'
        reservation.save()
        return reservation

    def cancel_reservation(self, pk):
        reservation = self.reservation_repo.get_by_id(pk)
        if reservation.status == 'CON' or reservation.status == 'PAID':
            raise ValidationError('Cannot cancel a confirmed or paid reservation directly. Refund process needed.')
        reservation.status = 'CAN'
        reservation.save()
        return reservation

    def get_reservations_list(self):
        return self.reservation_repo.get_all().order_by('-reservation_date')

    def update_reservation_status(self, reservation_pk, new_status):
        reservation = self.reservation_repo.get_by_id(reservation_pk)
        if new_status in [choice[0] for choice in Reservation.RESERVATION_STATUS_CHOICES]:
            reservation.status = new_status
            reservation.save()
        return reservation

    def get_flight_details_with_seats(self, flight_pk):
        flight = self.flight_repo.get_by_id(flight_pk)
        seats = self.seat_repo.filter_by_airplane_ordered(flight.airplane)
        reserved_seats_ids = self.reservation_repo.filter_by_flight_seat_status(flight, None, ['PEN', 'CON', 'PAID']).values_list('seat__id', flat=True)
        
        for seat in seats:
            seat.is_reserved = seat.id in reserved_seats_ids
        
        seats_by_row = {}
        for seat in seats:
            seats_by_row.setdefault(seat.row, []).append(seat)
        
        return flight, dict(sorted(seats_by_row.items()))

    def get_passengers_by_flight(self, flight_pk):
        flight = self.flight_repo.get_by_id(flight_pk)
        reservations = self.reservation_repo.filter_by_flight_and_select_related(flight).order_by('passenger__last_name', 'passenger__first_name')
        return flight, reservations

class SeatLayoutService:
    def __init__(self):
        self.seat_layout_repo = SeatLayoutRepository()
        self.seat_layout_position_repo = SeatLayoutPositionRepository()
        self.seat_type_repo = SeatTypeRepository()

    def create_seat_layout_with_positions(self, layout_name, rows, columns, positions_data):
        with transaction.atomic():
            seat_layout = self.seat_layout_repo.create({
                'layout_name': layout_name,
                'rows': rows,
                'columns': columns
            })
            for pos_data in positions_data:
                seat_type = self.seat_type_repo.get_by_id(pos_data['seat_type_id'])
                self.seat_layout_position_repo.create({
                    'seat_layout': seat_layout,
                    'seat_type': seat_type,
                    'row': pos_data['row'],
                    'column': pos_data['column']
                })
            return seat_layout

    def update_seat_layout(self, pk, data):
        return self.seat_layout_repo.update(pk, data)

    def delete_seat_layout(self, pk):
        return self.seat_layout_repo.delete(pk)

class SeatTypeService:
    def __init__(self):
        self.seat_type_repo = SeatTypeRepository()

    def create_seat_type(self, data):
        return self.seat_type_repo.create(data)

    def update_seat_type(self, pk, data):
        return self.seat_type_repo.update(pk, data)

    def delete_seat_type(self, pk):
        return self.seat_type_repo.delete(pk)

class SeatLayoutPositionService:
    def __init__(self):
        self.seat_layout_position_repo = SeatLayoutPositionRepository()

    def create_seat_layout_position(self, data):
        return self.seat_layout_position_repo.create(data)

    def update_seat_layout_position(self, pk, data):
        return self.seat_layout_position_repo.update(pk, data)

    def delete_seat_layout_position(self, pk):
        return self.seat_layout_position_repo.delete(pk)

class FlightHistoryService:
    def __init__(self):
        self.flight_history_repo = FlightHistoryRepository()
        self.passenger_repo = PassengerRepository()
        self.flight_repo = FlightRepository()

    def get_flight_history_by_passenger(self, passenger_id):
        passenger = self.passenger_repo.get_by_id(passenger_id)
        return self.flight_history_repo.filter_by_passenger_ordered(passenger)

    def get_flight_history_by_flight(self, flight_id):
        flight = self.flight_repo.get_by_id(flight_id)
        return self.flight_history_repo.filter_by_flight(flight.pk)

class TicketService:
    def __init__(self):
        self.ticket_repo = TicketRepository()
        self.reservation_repo = ReservationRepository()

    def issue_ticket(self, reservation_pk):
        reservation = self.reservation_repo.get_by_id(reservation_pk)
        if reservation.status not in ['CON', 'PAID']:
            raise ValidationError('Ticket can only be issued for confirmed or paid reservations.')
        
        ticket, created = self.ticket_repo.get_or_create_ticket(
            reservation=reservation,
            defaults={
                'barcode': str(uuid.uuid4()).replace('-', '')[:20],
                'status': 'EMI'
            }
        )
        return ticket

    def cancel_ticket(self, pk):
        ticket = self.ticket_repo.get_by_id(pk)
        if ticket.status == 'USED':
            raise ValidationError('Cannot cancel a used ticket.')
        ticket.status = 'CAN'
        ticket.save()
        return ticket

    def delete_ticket(self, pk):
        return self.ticket_repo.delete(pk)

    def get_ticket_detail(self, ticket_pk):
        return self.ticket_repo.get_by_id(ticket_pk)
