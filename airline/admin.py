from django.contrib import admin
from .models import Airplane, Flight, SeatLayout, SeatType, SeatLayoutPosition, Passenger, FlightHistory, Seat, Reservation, Ticket, UserProfile

admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(SeatLayout)
admin.site.register(SeatType)
admin.site.register(SeatLayoutPosition)
admin.site.register(Passenger)
admin.site.register(FlightHistory)
admin.site.register(Seat)
admin.site.register(Reservation)
admin.site.register(Ticket)
admin.site.register(UserProfile)
