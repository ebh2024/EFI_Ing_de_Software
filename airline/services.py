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
    """
    Servicio para gestionar operaciones relacionadas con aviones.

    Maneja la creación de aviones con asientos, actualizaciones y eliminaciones.
    """
    def __init__(self):
        """
        Inicializa el servicio con los repositorios necesarios.
        """
        self.airplane_repo = AirplaneRepository()
        self.seat_layout_repo = SeatLayoutRepository()
        self.seat_repo = SeatRepository()

    def create_airplane_with_seats(self, data):
        """
        Crea un avión y genera automáticamente los asientos basados en el layout.

        Parámetros:
            data (dict): Datos del avión, incluyendo opcionalmente 'seat_layout'.

        Retorna:
            Airplane: Instancia del avión creado.
        """
        seat_layout_id = data.pop('seat_layout', None)
        seat_layout = None
        if seat_layout_id:
            seat_layout = self.seat_layout_repo.get_by_id(seat_layout_id)
            data['seat_layout'] = seat_layout
        
        airplane = self.airplane_repo.create(data)

        if seat_layout:
            self._create_seats_for_airplane(airplane, seat_layout)
        return airplane

    def _create_seats_for_airplane(self, airplane, seat_layout):
        """
        Crea asientos para un avión basado en el layout de asientos.

        Parámetros:
            airplane (Airplane): Instancia del avión.
            seat_layout (SeatLayout): Layout de asientos a usar.

        Efectos secundarios:
            Crea múltiples instancias de Seat en la base de datos.
        """
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

    def update_airplane(self, pk, data):
        """
        Actualiza un avión existente.

        Parámetros:
            pk (int): Clave primaria del avión.
            data (dict): Datos actualizados.

        Retorna:
            Airplane: Instancia del avión actualizado.
        """
        seat_layout_id = data.pop('seat_layout', None)
        seat_layout = None
        if seat_layout_id:
            seat_layout = self.seat_layout_repo.get_by_id(seat_layout_id)
            data['seat_layout'] = seat_layout
        return self.airplane_repo.update(pk, data)

    def delete_airplane(self, pk):
        """
        Elimina un avión.

        Parámetros:
            pk (int): Clave primaria del avión.

        Retorna:
            bool: True si la eliminación fue exitosa.
        """
        return self.airplane_repo.delete(pk)

class FlightService:
    """
    Servicio para gestionar operaciones relacionadas con vuelos.

    Maneja creación, actualización, eliminación y consulta de asientos disponibles.
    """
    def __init__(self):
        """
        Inicializa el servicio con los repositorios necesarios.
        """
        self.flight_repo = FlightRepository()
        self.seat_repo = SeatRepository()
        self.reservation_repo = ReservationRepository()

    def create_flight(self, data):
        """
        Crea un nuevo vuelo.

        Parámetros:
            data (dict): Datos del vuelo.

        Retorna:
            Flight: Instancia del vuelo creado.
        """
        return self.flight_repo.create(data)

    def update_flight(self, pk, data):
        """
        Actualiza un vuelo existente.

        Parámetros:
            pk (int): Clave primaria del vuelo.
            data (dict): Datos actualizados.

        Retorna:
            Flight: Instancia del vuelo actualizado.
        """
        return self.flight_repo.update(pk, data)

    def delete_flight(self, pk):
        """
        Elimina un vuelo.

        Parámetros:
            pk (int): Clave primaria del vuelo.

        Retorna:
            bool: True si la eliminación fue exitosa.
        """
        return self.flight_repo.delete(pk)

    def get_available_seats(self, flight_pk):
        """
        Obtiene los asientos disponibles para un vuelo.

        Parámetros:
            flight_pk (int): Clave primaria del vuelo.

        Retorna:
            list: Lista de asientos disponibles.
        """
        flight = self.flight_repo.get_by_id(flight_pk)
        all_seats = self.seat_repo.filter_by_airplane_ordered(flight.airplane)
        reserved_seats_ids = self.reservation_repo.filter_by_flight_seat_status(flight, None, ['PEN', 'CON', 'PAID']).values_list('seat__id', flat=True)
        
        available_seats = [seat for seat in all_seats if seat.id not in reserved_seats_ids]
        return available_seats

class PassengerService:
    """
    Servicio para gestionar operaciones relacionadas con pasajeros.

    Maneja creación, actualización, eliminación y consulta de historial de vuelos.
    """
    def __init__(self):
        """
        Inicializa el servicio con los repositorios necesarios.
        """
        self.passenger_repo = PassengerRepository()
        self.flight_history_repo = FlightHistoryRepository()

    def create_passenger(self, data):
        """
        Crea un nuevo pasajero.

        Parámetros:
            data (dict): Datos del pasajero.

        Retorna:
            Passenger: Instancia del pasajero creado.
        """
        return self.passenger_repo.create(data)

    def update_passenger(self, pk, data):
        """
        Actualiza un pasajero existente.

        Parámetros:
            pk (int): Clave primaria del pasajero.
            data (dict): Datos actualizados.

        Retorna:
            Passenger: Instancia del pasajero actualizado.
        """
        return self.passenger_repo.update(pk, data)

    def delete_passenger(self, pk):
        """
        Elimina un pasajero.

        Parámetros:
            pk (int): Clave primaria del pasajero.

        Retorna:
            bool: True si la eliminación fue exitosa.
        """
        return self.passenger_repo.delete(pk)

    def get_or_create_passenger_for_user(self, user):
        """
        Obtiene o crea un pasajero basado en un usuario del sistema.

        Parámetros:
            user (User): Instancia del usuario.

        Retorna:
            Passenger: Instancia del pasajero.
        """
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
        """
        Obtiene el historial de vuelos de un pasajero.

        Parámetros:
            passenger_pk (int): Clave primaria del pasajero.

        Retorna:
            tuple: (Passenger, QuerySet) - Pasajero e historial de vuelos.
        """
        passenger = self.passenger_repo.get_by_id(passenger_pk)
        flight_history = self.flight_history_repo.filter_by_passenger_ordered(passenger)
        return passenger, flight_history

class ReservationService:
    """
    Servicio para gestionar operaciones relacionadas con reservas.

    Maneja creación, confirmación, cancelación y consulta de reservas y asientos.
    """
    def __init__(self):
        """
        Inicializa el servicio con los repositorios necesarios.
        """
        self.reservation_repo = ReservationRepository()
        self.flight_repo = FlightRepository()
        self.passenger_repo = PassengerRepository()
        self.seat_repo = SeatRepository()

    def create_reservation(self, flight_id, passenger_id, seat_id, price):
        """
        Crea una nueva reserva para un vuelo.

        Parámetros:
            flight_id (int): ID del vuelo.
            passenger_id (int): ID del pasajero.
            seat_id (int): ID del asiento.
            price (Decimal): Precio de la reserva.

        Retorna:
            Reservation: Instancia de la reserva creada.

        Raises:
            ValidationError: Si el asiento ya está reservado.
        """
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
            self._update_seat_status_to_reserved(seat)
            return reservation

    def _update_seat_status_to_reserved(self, seat):
        """
        Actualiza el estado de un asiento a reservado.

        Parámetros:
            seat (Seat): Instancia del asiento.

        Efectos secundarios:
            Modifica y guarda el estado del asiento.
        """
        seat.status = 'Reserved'
        self.seat_repo.update(seat.pk, {'status': 'Reserved'})

    def update_reservation(self, pk, data):
        """
        Actualiza una reserva existente.

        Parámetros:
            pk (int): Clave primaria de la reserva.
            data (dict): Datos actualizados.

        Retorna:
            Reservation: Instancia de la reserva actualizada.
        """
        return self.reservation_repo.update(pk, data)

    def delete_reservation(self, pk):
        """
        Elimina una reserva y libera el asiento.

        Parámetros:
            pk (int): Clave primaria de la reserva.

        Retorna:
            bool: True si la eliminación fue exitosa.

        Efectos secundarios:
            Cambia el estado del asiento asociado a 'Available'.
        """
        reservation = self.reservation_repo.get_by_id(pk)
        with transaction.atomic():
            self.reservation_repo.delete(pk)
            self.seat_repo.update(reservation.seat.pk, {'status': 'Available'})
        return True

    def confirm_reservation(self, pk):
        """
        Confirma una reserva pendiente.

        Parámetros:
            pk (int): Clave primaria de la reserva.

        Retorna:
            Reservation: Instancia de la reserva confirmada.

        Raises:
            ValidationError: Si la reserva está cancelada.
        """
        reservation = self.reservation_repo.get_by_id(pk)
        if reservation.status == 'CAN':
            raise ValidationError('Cannot confirm a cancelled reservation.')
        reservation.status = 'CON'
        reservation.save()
        return reservation

    def cancel_reservation(self, pk):
        """
        Cancela una reserva pendiente.

        Parámetros:
            pk (int): Clave primaria de la reserva.

        Retorna:
            Reservation: Instancia de la reserva cancelada.

        Raises:
            ValidationError: Si la reserva ya está confirmada o pagada.
        """
        reservation = self.reservation_repo.get_by_id(pk)
        if reservation.status == 'CON' or reservation.status == 'PAID':
            raise ValidationError('Cannot cancel a confirmed or paid reservation directly. Refund process needed.')
        reservation.status = 'CAN'
        reservation.save()
        return reservation

    def get_reservations_list(self):
        """
        Obtiene la lista de todas las reservas ordenadas por fecha.

        Retorna:
            QuerySet: Reservas ordenadas por fecha de reserva descendente.
        """
        return self.reservation_repo.get_all().order_by('-reservation_date')

    def update_reservation_status(self, reservation_pk, new_status):
        """
        Actualiza el estado de una reserva.

        Parámetros:
            reservation_pk (int): Clave primaria de la reserva.
            new_status (str): Nuevo estado para la reserva.

        Retorna:
            Reservation: Instancia de la reserva actualizada.
        """
        reservation = self.reservation_repo.get_by_id(reservation_pk)
        if new_status in [choice[0] for choice in Reservation.RESERVATION_STATUS_CHOICES]:
            reservation.status = new_status
            reservation.save()
        return reservation

    def get_flight_details_with_seats(self, flight_pk):
        """
        Obtiene detalles de un vuelo incluyendo asientos organizados por fila.

        Parámetros:
            flight_pk (int): Clave primaria del vuelo.

        Retorna:
            tuple: (Flight, dict) - Vuelo y asientos organizados por fila.
        """
        flight = self.flight_repo.get_by_id(flight_pk)
        seats = self.seat_repo.filter_by_airplane_ordered(flight.airplane)
        reserved_seats_ids = self.reservation_repo.filter_by_flight_seat_status(flight, None, ['PEN', 'CON', 'PAID']).values_list('seat__id', flat=True)
        
        seats = self._mark_reserved_seats(seats, reserved_seats_ids)
        seats_by_row = self._organize_seats_by_row(seats)
        
        return flight, dict(sorted(seats_by_row.items()))

    def _mark_reserved_seats(self, seats, reserved_seats_ids):
        """
        Marca los asientos reservados en una lista de asientos.

        Parámetros:
            seats (list): Lista de asientos.
            reserved_seats_ids (list): IDs de asientos reservados.

        Retorna:
            list: Lista de asientos con atributo is_reserved.
        """
        for seat in seats:
            seat.is_reserved = seat.id in reserved_seats_ids
        return seats

    def _organize_seats_by_row(self, seats):
        """
        Organiza los asientos por fila.

        Parámetros:
            seats (list): Lista de asientos.

        Retorna:
            dict: Asientos organizados por número de fila.
        """
        seats_by_row = {}
        for seat in seats:
            seats_by_row.setdefault(seat.row, []).append(seat)
        return seats_by_row

    def get_passengers_by_flight(self, flight_pk):
        """
        Obtiene la lista de pasajeros de un vuelo.

        Parámetros:
            flight_pk (int): Clave primaria del vuelo.

        Retorna:
            tuple: (Flight, QuerySet) - Vuelo y reservas con pasajeros relacionados.
        """
        flight = self.flight_repo.get_by_id(flight_pk)
        reservations = self.reservation_repo.filter_by_flight_and_select_related(flight).order_by('passenger__last_name', 'passenger__first_name')
        return flight, reservations

class SeatLayoutService:
    """
    Servicio para gestionar operaciones relacionadas con layouts de asientos.

    Maneja creación con posiciones, actualizaciones y eliminaciones.
    """
    def __init__(self):
        """
        Inicializa el servicio con los repositorios necesarios.
        """
        self.seat_layout_repo = SeatLayoutRepository()
        self.seat_layout_position_repo = SeatLayoutPositionRepository()
        self.seat_type_repo = SeatTypeRepository()

    def create_seat_layout_with_positions(self, layout_name, rows, columns, positions_data):
        """
        Crea un layout de asientos con sus posiciones.

        Parámetros:
            layout_name (str): Nombre del layout.
            rows (int): Número de filas.
            columns (int): Número de columnas.
            positions_data (list): Datos de posiciones con tipos de asiento.

        Retorna:
            SeatLayout: Instancia del layout creado.
        """
        with transaction.atomic():
            seat_layout = self.seat_layout_repo.create({
                'layout_name': layout_name,
                'rows': rows,
                'columns': columns
            })
            self._create_seat_layout_positions(seat_layout, positions_data)
            return seat_layout

    def _create_seat_layout_positions(self, seat_layout, positions_data):
        """
        Crea posiciones para un layout de asientos.

        Parámetros:
            seat_layout (SeatLayout): Instancia del layout.
            positions_data (list): Lista de datos de posiciones.

        Efectos secundarios:
            Crea múltiples instancias de SeatLayoutPosition.
        """
        for pos_data in positions_data:
            seat_type = self.seat_type_repo.get_by_id(pos_data['seat_type_id'])
            self.seat_layout_position_repo.create({
                'seat_layout': seat_layout,
                'seat_type': seat_type,
                'row': pos_data['row'],
                'column': pos_data['column']
            })

    def update_seat_layout(self, pk, data):
        """
        Actualiza un layout de asientos existente.

        Parámetros:
            pk (int): Clave primaria del layout.
            data (dict): Datos actualizados.

        Retorna:
            SeatLayout: Instancia del layout actualizado.
        """
        return self.seat_layout_repo.update(pk, data)

    def delete_seat_layout(self, pk):
        """
        Elimina un layout de asientos.

        Parámetros:
            pk (int): Clave primaria del layout.

        Retorna:
            bool: True si la eliminación fue exitosa.
        """
        return self.seat_layout_repo.delete(pk)

class SeatTypeService:
    """
    Servicio para gestionar operaciones relacionadas con tipos de asientos.

    Maneja creación, actualización y eliminación de tipos de asiento.
    """
    def __init__(self):
        """
        Inicializa el servicio con el repositorio necesario.
        """
        self.seat_type_repo = SeatTypeRepository()

    def create_seat_type(self, data):
        """
        Crea un nuevo tipo de asiento.

        Parámetros:
            data (dict): Datos del tipo de asiento.

        Retorna:
            SeatType: Instancia del tipo de asiento creado.
        """
        return self.seat_type_repo.create(data)

    def update_seat_type(self, pk, data):
        """
        Actualiza un tipo de asiento existente.

        Parámetros:
            pk (int): Clave primaria del tipo de asiento.
            data (dict): Datos actualizados.

        Retorna:
            SeatType: Instancia del tipo de asiento actualizado.
        """
        return self.seat_type_repo.update(pk, data)

    def delete_seat_type(self, pk):
        """
        Elimina un tipo de asiento.

        Parámetros:
            pk (int): Clave primaria del tipo de asiento.

        Retorna:
            bool: True si la eliminación fue exitosa.
        """
        return self.seat_type_repo.delete(pk)

class SeatLayoutPositionService:
    """
    Servicio para gestionar operaciones relacionadas con posiciones de layouts de asientos.

    Maneja creación, actualización y eliminación de posiciones.
    """
    def __init__(self):
        """
        Inicializa el servicio con el repositorio necesario.
        """
        self.seat_layout_position_repo = SeatLayoutPositionRepository()

    def create_seat_layout_position(self, data):
        """
        Crea una nueva posición en un layout de asientos.

        Parámetros:
            data (dict): Datos de la posición.

        Retorna:
            SeatLayoutPosition: Instancia de la posición creada.
        """
        return self.seat_layout_position_repo.create(data)

    def update_seat_layout_position(self, pk, data):
        """
        Actualiza una posición de layout existente.

        Parámetros:
            pk (int): Clave primaria de la posición.
            data (dict): Datos actualizados.

        Retorna:
            SeatLayoutPosition: Instancia de la posición actualizada.
        """
        return self.seat_layout_position_repo.update(pk, data)

    def delete_seat_layout_position(self, pk):
        """
        Elimina una posición de layout de asientos.

        Parámetros:
            pk (int): Clave primaria de la posición.

        Retorna:
            bool: True si la eliminación fue exitosa.
        """
        return self.seat_layout_position_repo.delete(pk)

class FlightHistoryService:
    """
    Servicio para gestionar consultas de historial de vuelos.

    Permite obtener historial por pasajero o por vuelo.
    """
    def __init__(self):
        """
        Inicializa el servicio con los repositorios necesarios.
        """
        self.flight_history_repo = FlightHistoryRepository()
        self.passenger_repo = PassengerRepository()
        self.flight_repo = FlightRepository()

    def get_flight_history_by_passenger(self, passenger_id):
        """
        Obtiene el historial de vuelos de un pasajero.

        Parámetros:
            passenger_id (int): ID del pasajero.

        Retorna:
            QuerySet: Historial de vuelos del pasajero ordenado.
        """
        passenger = self.passenger_repo.get_by_id(passenger_id)
        return self.flight_history_repo.filter_by_passenger_ordered(passenger)

    def get_flight_history_by_flight(self, flight_id):
        """
        Obtiene el historial de vuelos de un vuelo específico.

        Parámetros:
            flight_id (int): ID del vuelo.

        Retorna:
            QuerySet: Historial de vuelos del vuelo.
        """
        flight = self.flight_repo.get_by_id(flight_id)
        return self.flight_history_repo.filter_by_flight(flight.pk)

class TicketService:
    """
    Servicio para gestionar operaciones relacionadas con tickets.

    Maneja emisión, cancelación y consulta de tickets.
    """
    def __init__(self):
        """
        Inicializa el servicio con los repositorios necesarios.
        """
        self.ticket_repo = TicketRepository()
        self.reservation_repo = ReservationRepository()

    def issue_ticket(self, reservation_pk):
        """
        Emite un ticket para una reserva confirmada o pagada.

        Parámetros:
            reservation_pk (int): Clave primaria de la reserva.

        Retorna:
            Ticket: Instancia del ticket emitido.

        Raises:
            ValidationError: Si la reserva no está en estado válido.
        """
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
        """
        Cancela un ticket.

        Parámetros:
            pk (int): Clave primaria del ticket.

        Retorna:
            Ticket: Instancia del ticket cancelado.

        Raises:
            ValidationError: Si el ticket ya está usado.
        """
        ticket = self.ticket_repo.get_by_id(pk)
        if ticket.status == 'USED':
            raise ValidationError('Cannot cancel a used ticket.')
        ticket.status = 'CAN'
        ticket.save()
        return ticket

    def delete_ticket(self, pk):
        """
        Elimina un ticket.

        Parámetros:
            pk (int): Clave primaria del ticket.

        Retorna:
            bool: True si la eliminación fue exitosa.
        """
        return self.ticket_repo.delete(pk)

    def get_ticket_detail(self, ticket_pk):
        """
        Obtiene los detalles de un ticket.

        Parámetros:
            ticket_pk (int): Clave primaria del ticket.

        Retorna:
            Ticket: Instancia del ticket.
        """
        return self.ticket_repo.get_by_id(ticket_pk)
