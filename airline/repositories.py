from django.shortcuts import get_object_or_404
from .models import Airplane, Flight, Passenger, Reservation, Seat, SeatLayout, SeatType, SeatLayoutPosition, FlightHistory, Ticket

class BaseRepository:
    """
    Clase base para repositorios que proporciona operaciones CRUD básicas.

    Atributos:
        model: Modelo de Django que maneja el repositorio.
    """
    model = None

    def get_by_id(self, pk):
        """
        Obtiene un objeto por su clave primaria.

        Parámetros:
            pk: Clave primaria del objeto.

        Retorna:
            Instancia del modelo o lanza Http404 si no existe.
        """
        return get_object_or_404(self.model, pk=pk)

    def get_all(self):
        """
        Obtiene todos los objetos del modelo.

        Retorna:
            QuerySet: Todos los objetos del modelo.
        """
        return self.model.objects.all()

    def create(self, data):
        """
        Crea un nuevo objeto con los datos proporcionados.

        Parámetros:
            data (dict): Datos para crear el objeto.

        Retorna:
            Instancia del modelo creado.
        """
        return self.model.objects.create(**data)

    def update(self, pk, data):
        """
        Actualiza un objeto existente con los datos proporcionados.

        Parámetros:
            pk: Clave primaria del objeto.
            data (dict): Datos para actualizar.

        Retorna:
            Instancia del modelo actualizado.
        """
        obj = self.get_by_id(pk)
        for attr, value in data.items():
            setattr(obj, attr, value)
        obj.save()
        return obj

    def delete(self, pk):
        """
        Elimina un objeto por su clave primaria.

        Parámetros:
            pk: Clave primaria del objeto.

        Retorna:
            bool: True si la eliminación fue exitosa.
        """
        obj = self.get_by_id(pk)
        obj.delete()
        return True

class AirplaneRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de aviones.

    Hereda operaciones CRUD básicas de BaseRepository.
    """
    model = Airplane

class FlightRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de vuelos.

    Hereda operaciones CRUD básicas de BaseRepository.
    """
    model = Flight

class PassengerRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de pasajeros.

    Hereda operaciones CRUD básicas y añade método para obtener o crear pasajero.
    """
    model = Passenger

    def get_or_create_passenger(self, email, defaults):
        """
        Obtiene o crea un pasajero basado en el email.

        Parámetros:
            email (str): Email del pasajero.
            defaults (dict): Valores por defecto si se crea.

        Retorna:
            tuple: (Passenger, bool) - Instancia y si fue creado.
        """
        return self.model.objects.get_or_create(email=email, defaults=defaults)

class ReservationRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de reservas.

    Hereda operaciones CRUD básicas y añade métodos de filtrado.
    """
    model = Reservation

    def filter_by_flight_seat_status(self, flight, seat, statuses):
        """
        Filtra reservas por vuelo, asiento y estados.

        Parámetros:
            flight (Flight): Instancia del vuelo.
            seat (Seat): Instancia del asiento.
            statuses (list): Lista de estados a filtrar.

        Retorna:
            QuerySet: Reservas que coinciden con los criterios.
        """
        return self.model.objects.filter(flight=flight, seat=seat, status__in=statuses)

    def filter_by_flight_and_select_related(self, flight):
        """
        Filtra reservas por vuelo con relaciones select_related.

        Parámetros:
            flight (Flight): Instancia del vuelo.

        Retorna:
            QuerySet: Reservas del vuelo con pasajero y asiento relacionados.
        """
        return self.model.objects.filter(flight=flight).select_related('passenger', 'seat')

class SeatRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de asientos.

    Hereda operaciones CRUD básicas y añade método de filtrado ordenado.
    """
    model = Seat

    def filter_by_airplane_ordered(self, airplane):
        """
        Filtra asientos por avión ordenados por fila y columna.

        Parámetros:
            airplane (Airplane): Instancia del avión.

        Retorna:
            QuerySet: Asientos del avión ordenados.
        """
        return self.model.objects.filter(airplane=airplane).order_by('row', 'column')

class SeatLayoutRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de layouts de asientos.

    Hereda operaciones CRUD básicas de BaseRepository.
    """
    model = SeatLayout

class SeatTypeRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de tipos de asientos.

    Hereda operaciones CRUD básicas de BaseRepository.
    """
    model = SeatType

class SeatLayoutPositionRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de posiciones de layouts de asientos.

    Hereda operaciones CRUD básicas de BaseRepository.
    """
    model = SeatLayoutPosition

class FlightHistoryRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de historial de vuelos.

    Hereda operaciones CRUD básicas y añade métodos de filtrado.
    """
    model = FlightHistory

    def filter_by_passenger_ordered(self, passenger):
        """
        Filtra historial de vuelos por pasajero ordenado por fecha descendente.

        Parámetros:
            passenger (Passenger): Instancia del pasajero.

        Retorna:
            QuerySet: Historial ordenado por fecha de reserva.
        """
        return self.model.objects.filter(passenger=passenger).order_by('-booking_date')

    def filter_by_flight(self, flight_id):
        """
        Filtra historial de vuelos por ID de vuelo.

        Parámetros:
            flight_id (int): ID del vuelo.

        Retorna:
            QuerySet: Historial del vuelo.
        """
        return self.model.objects.filter(flight__id=flight_id)

    def filter_by_passenger(self, passenger_id):
        """
        Filtra historial de vuelos por ID de pasajero.

        Parámetros:
            passenger_id (int): ID del pasajero.

        Retorna:
            QuerySet: Historial del pasajero.
        """
        return self.model.objects.filter(passenger__id=passenger_id)

class TicketRepository(BaseRepository):
    """
    Repositorio para gestionar operaciones de tickets.

    Hereda operaciones CRUD básicas y añade método para obtener o crear ticket.
    """
    model = Ticket

    def get_or_create_ticket(self, reservation, defaults):
        """
        Obtiene o crea un ticket basado en la reserva.

        Parámetros:
            reservation (Reservation): Instancia de la reserva.
            defaults (dict): Valores por defecto si se crea.

        Retorna:
            tuple: (Ticket, bool) - Instancia y si fue creado.
        """
        return self.model.objects.get_or_create(reservation=reservation, defaults=defaults)
