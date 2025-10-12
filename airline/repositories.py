from .models import (
    Airplane, Flight, Passenger, Reservation, Seat, Ticket,
    SeatLayout, SeatLayoutPosition, SeatType, FlightHistory
)

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, obj_id):
        try:
            return self.model.objects.get(pk=obj_id)
        except self.model.DoesNotExist:
            return None

    def get_all(self):
        return self.model.objects.all()

    def filter(self, **kwargs):
        return self.model.objects.filter(**kwargs)

    def create(self, data):
        obj = self.model(**data)
        obj.full_clean() # Validate model fields
        obj.save()
        return obj

    def update(self, obj_id, data):
        obj = self.get_by_id(obj_id)
        if not obj:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        obj.full_clean() # Validate model fields
        obj.save()
        return obj

    def delete(self, obj_id):
        obj = self.get_by_id(obj_id)
        if not obj:
            return False
        obj.delete()
        return True

class AirplaneRepository(BaseRepository):
    def __init__(self):
        super().__init__(Airplane)

class FlightRepository(BaseRepository):
    def __init__(self):
        super().__init__(Flight)

class PassengerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Passenger)

class ReservationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Reservation)

class SeatRepository(BaseRepository):
    def __init__(self):
        super().__init__(Seat)

class TicketRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ticket)

class SeatLayoutRepository(BaseRepository):
    def __init__(self):
        super().__init__(SeatLayout)

class SeatLayoutPositionRepository(BaseRepository):
    def __init__(self):
        super().__init__(SeatLayoutPosition)

class SeatTypeRepository(BaseRepository):
    def __init__(self):
        super().__init__(SeatType)

class FlightHistoryRepository(BaseRepository):
    def __init__(self):
        super().__init__(FlightHistory)
