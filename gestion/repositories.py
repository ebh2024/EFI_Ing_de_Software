from .models import Vuelo, Pasajero, Avion, Reserva, Asiento

class VueloRepository:
    def get_all(self):
        return Vuelo.objects.all()

    def get_by_id(self, vuelo_id):
        return Vuelo.objects.get(pk=vuelo_id)

class PasajeroRepository:
    def get_by_user(self, user):
        return Pasajero.objects.get(user=user)

    def create(self, user, nombre, apellido, documento, email, telefono):
        return Pasajero.objects.create(
            user=user,
            nombre=nombre,
            apellido=apellido,
            documento=documento,
            email=email,
            telefono=telefono
        )

class AsientoRepository:
    def get_by_id(self, asiento_id):
        return Asiento.objects.get(pk=asiento_id)

    def get_by_vuelo(self, vuelo):
        return Asiento.objects.filter(vuelo=vuelo)

    def save(self, asiento):
        asiento.save()

class ReservaRepository:
    def create(self, vuelo, pasajero, asiento):
        return Reserva.objects.create(
            vuelo=vuelo,
            pasajero=pasajero,
            asiento=asiento
        )

    def get_by_id(self, reserva_id):
        return Reserva.objects.get(pk=reserva_id)

    def get_by_vuelo(self, vuelo):
        return Reserva.objects.filter(vuelo=vuelo)
