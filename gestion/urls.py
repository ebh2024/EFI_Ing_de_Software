from django.urls import path
from . import views

# Definición de patrones de URL para la aplicación 'gestion'.
urlpatterns = [
    # Ruta para la lista de vuelos (página de inicio).
    path('', views.flight_list, name='flight_list'),
    # Ruta para los detalles de un vuelo específico.
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    # Ruta para reservar un asiento en un vuelo.
    path('book/<int:seat_id>/', views.book_seat, name='book_seat'),
    # Ruta para ver los detalles de un boleto/reserva.
    path('ticket/<int:booking_id>/', views.ticket, name='ticket'),
    # Ruta para el reporte de pasajeros por vuelo (solo para staff).
    path('report/flight/<int:flight_id>/', views.passenger_report_by_flight, name='passenger_report_by_flight'),
    # Ruta para crear un nuevo pasajero.
    path('passenger/create/', views.create_passenger, name='create_passenger'),
    # Ruta para el perfil del usuario.
    path('profile/', views.user_profile, name='user_profile'),
    # Ruta para editar el perfil del usuario.
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # Ruta para ver las notificaciones del usuario.
    path('notifications/', views.notifications, name='notifications'),
    # Ruta para marcar una notificación como leída.
    path('notifications/mark_read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    # Ruta para procesar el pago de una reserva.
    path('payment/<int:booking_id>/', views.process_payment, name='process_payment'),
    # Ruta para cancelar una reserva.
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
