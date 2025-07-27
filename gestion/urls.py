from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_vuelos, name='lista_vuelos'),
    path('vuelo/<int:vuelo_id>/', views.detalle_vuelo, name='detalle_vuelo'),
    path('reservar/<int:asiento_id>/', views.reservar_asiento, name='reservar_asiento'),
    path('boleto/<int:reserva_id>/', views.boleto, name='boleto'),
]
