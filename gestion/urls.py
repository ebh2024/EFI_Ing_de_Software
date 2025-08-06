from django.urls import path
from . import views

urlpatterns = [
    path('', views.flight_list, name='flight_list'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('book/<int:seat_id>/', views.book_seat, name='book_seat'),
    path('ticket/<int:booking_id>/', views.ticket, name='ticket'),
    path('report/flight/<int:flight_id>/', views.passenger_report_by_flight, name='passenger_report_by_flight'),
    path('passenger/create/', views.create_passenger, name='create_passenger'),
]
