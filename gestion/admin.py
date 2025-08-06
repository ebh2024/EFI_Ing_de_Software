from django.contrib import admin
from .models import Flight, Passenger, Booking, Aircraft, Seat

class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1

class PassengerAdmin(admin.ModelAdmin):
    inlines = [BookingInline]

admin.site.register(Flight)
admin.site.register(Passenger, PassengerAdmin)
admin.site.register(Booking)
admin.site.register(Aircraft)
admin.site.register(Seat)
