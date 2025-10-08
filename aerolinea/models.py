from django.db import models

class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    filas = models.IntegerField()
    columnas = models.IntegerField()

    def __str__(self):
        return f"{self.modelo} ({self.capacidad} asientos)"

class Vuelo(models.Model):
    avion = models.ForeignKey(Avion, on_delete=models.CASCADE)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    duracion = models.DurationField()
    estado = models.CharField(max_length=50)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Vuelo {self.origen} a {self.destino} el {self.fecha_salida.strftime('%Y-%m-%d %H:%M')}"

class Pasajero(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'Documento Nacional de Identidad'),
        ('PAS', 'Pasaporte'),
        ('LE', 'Libreta de Enrolamiento'),
        ('LC', 'Libreta Cívica'),
    ]
    nombre = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOCUMENTO_CHOICES, default='DNI')

    def __str__(self):
        return self.nombre

class Asiento(models.Model):
    TIPO_ASIENTO_CHOICES = [
        ('ECO', 'Económico'),
        ('PRE', 'Premium'),
        ('EJE', 'Ejecutivo'),
    ]
    avion = models.ForeignKey(Avion, on_delete=models.CASCADE)
    numero = models.CharField(max_length=10)
    fila = models.IntegerField()
    columna = models.CharField(max_length=2)
    tipo = models.CharField(max_length=3, choices=TIPO_ASIENTO_CHOICES, default='ECO')
    estado = models.CharField(max_length=20) # Ej: 'Disponible', 'Ocupado', 'Reservado'

    def __str__(self):
        return f"Asiento {self.numero} - {self.avion.modelo}"

class Reserva(models.Model):
    ESTADO_RESERVA_CHOICES = [
        ('PEN', 'Pendiente'),
        ('CON', 'Confirmada'),
        ('CAN', 'Cancelada'),
        ('PAG', 'Pagada'),
    ]
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE)
    asiento = models.OneToOneField(Asiento, on_delete=models.CASCADE)
    estado = models.CharField(max_length=3, choices=ESTADO_RESERVA_CHOICES, default='PEN')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_reserva = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Reserva {self.codigo_reserva} para {self.pasajero.nombre} en vuelo {self.vuelo.id}"

class Usuario(models.Model):
    ROL_CHOICES = [
        ('ADM', 'Administrador'),
        ('EMP', 'Empleado'),
        ('CLI', 'Cliente'),
    ]
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128) # Se recomienda usar un hash de la contraseña
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=3, choices=ROL_CHOICES, default='CLI')

    def __str__(self):
        return self.username

class Boleto(models.Model):
    ESTADO_BOLETO_CHOICES = [
        ('EMI', 'Emitido'),
        ('CAN', 'Cancelado'),
        ('USA', 'Usado'),
    ]
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    codigo_barra = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=3, choices=ESTADO_BOLETO_CHOICES, default='EMI')

    def __str__(self):
        return f"Boleto {self.codigo_barra} para reserva {self.reserva.codigo_reserva}"
