from django.contrib import admin
from .models import Vuelo, Pasajero, Reserva, Avion

admin.site.register(Vuelo)
admin.site.register(Pasajero)
admin.site.register(Reserva)
admin.site.register(Avion)
