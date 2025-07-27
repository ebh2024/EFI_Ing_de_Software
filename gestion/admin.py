from django.contrib import admin
from .models import Vuelo, Pasajero, Reserva, Avion

class ReservaInline(admin.TabularInline):
    model = Reserva
    extra = 1

class PasajeroAdmin(admin.ModelAdmin):
    inlines = [ReservaInline]

admin.site.register(Vuelo)
admin.site.register(Pasajero, PasajeroAdmin)
admin.site.register(Reserva)
admin.site.register(Avion)
