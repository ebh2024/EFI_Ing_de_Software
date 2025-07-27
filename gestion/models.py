from django.db import models
from django.contrib.auth.models import User

class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.IntegerField()

    def __str__(self):
        return self.modelo

class Vuelo(models.Model):
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    avion = models.ForeignKey(Avion, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.origen} a {self.destino}"

class Pasajero(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, null=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def historial_vuelos(self):
        return self.reserva_set.all()

class Asiento(models.Model):
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('ocupado', 'Ocupado'),
    )
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    numero = models.CharField(max_length=10)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')

    def __str__(self):
        return f"Asiento {self.numero} en vuelo {self.vuelo}"

class Reserva(models.Model):
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE)
    asiento = models.OneToOneField(Asiento, on_delete=models.CASCADE, null=True)
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva de {self.pasajero} en vuelo {self.vuelo}, asiento {self.asiento.numero}"
