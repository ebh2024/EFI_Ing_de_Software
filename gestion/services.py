from .repositories import VueloRepository, PasajeroRepository, AsientoRepository, ReservaRepository
from django.contrib.auth.models import User
import secrets
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string

class VueloService:
    def __init__(self):
        self.vuelo_repository = VueloRepository()
        self.asiento_repository = AsientoRepository()
        self.reserva_repository = ReservaRepository()

    def get_all_vuelos(self):
        return self.vuelo_repository.get_all()

    def get_vuelo_details(self, vuelo_id):
        vuelo = self.vuelo_repository.get_by_id(vuelo_id)
        asientos = self.asiento_repository.get_by_vuelo(vuelo)
        return vuelo, asientos

    def get_reporte_pasajeros(self, vuelo_id):
        vuelo = self.vuelo_repository.get_by_id(vuelo_id)
        reservas = self.reserva_repository.get_by_vuelo(vuelo)
        return vuelo, reservas

class PasajeroService:
    def __init__(self):
        self.pasajero_repository = PasajeroRepository()

    def create_pasajero(self, nombre, apellido, documento, email, telefono):
        # Crear un nuevo usuario
        user = User.objects.create_user(
            username=email,
            email=email,
            password=''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
        )
        return self.pasajero_repository.create(user, nombre, apellido, documento, email, telefono)

class ReservaService:
    def __init__(self):
        self.asiento_repository = AsientoRepository()
        self.reserva_repository = ReservaRepository()
        self.pasajero_repository = PasajeroRepository()

    def reservar_asiento(self, asiento_id, user):
        asiento = self.asiento_repository.get_by_id(asiento_id)
        if asiento.estado != 'disponible':
            raise Exception("Este asiento no está disponible.")
        
        pasajero = self.pasajero_repository.get_by_user(user)
        
        if self.reserva_repository.get_by_vuelo(asiento.vuelo).filter(pasajero=pasajero).exists():
            raise Exception("Ya tienes una reserva en este vuelo.")
            
        asiento.estado = 'reservado'
        self.asiento_repository.save(asiento)
        
        reserva = self.reserva_repository.create(asiento.vuelo, pasajero, asiento)
        
        # Enviar correo electrónico
        mensaje = render_to_string('gestion/boleto_email.html', {'reserva': reserva})
        send_mail(
            'Confirmación de tu reserva',
            mensaje,
            'no-reply@aerolinea.com',
            [pasajero.email],
            fail_silently=False,
        )
        
        return reserva

    def get_boleto(self, reserva_id):
        return self.reserva_repository.get_by_id(reserva_id)
