from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

router = DefaultRouter()
router.register(r'airplanes', api_views.AirplaneViewSet, basename='airplane')
router.register(r'flights', api_views.FlightViewSet, basename='flight')
router.register(r'passengers', api_views.PassengerViewSet, basename='passenger')
router.register(r'reservations', api_views.ReservationViewSet, basename='reservation')
router.register(r'seat_layouts', api_views.SeatLayoutViewSet, basename='seatlayout')
router.register(r'seat_types', api_views.SeatTypeViewSet, basename='seattype')
router.register(r'seat_layout_positions', api_views.SeatLayoutPositionViewSet, basename='seatlayoutposition')
router.register(r'flight_history', api_views.FlightHistoryViewSet, basename='flighthistory')
router.register(r'tickets', api_views.TicketViewSet, basename='ticket')


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='airline/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('register/', views.register, name='register'),

    path('flights/', views.flight_list, name='flight_list'),
    path('flights/create/', views.flight_create, name='flight_create'),
    path('flights/update/<int:pk>/', views.flight_update, name='flight_update'),
    path('flights/delete/<int:pk>/', views.flight_delete, name='flight_delete'),

    path('passengers/', views.passenger_list, name='passenger_list'),
    path('passengers/create/', views.passenger_create, name='passenger_create'),
    path('passengers/update/<int:pk>/', views.passenger_update, name='passenger_update'),
    path('passengers/delete/<int:pk>/', views.passenger_delete, name='passenger_delete'),
    path('passengers/<int:pk>/history/', views.passenger_flight_history, name='passenger_flight_history'),

    # Reservation System URLs
    path('flights/<int:pk>/seats/', views.flight_detail_with_seats, name='flight_detail_with_seats'),
    path('flights/<int:flight_pk>/seats/<int:seat_pk>/reserve/', views.reserve_seat, name='reserve_seat'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:pk>/update_status/<str:new_status>/', views.reservation_update_status, name='reservation_update_status'),
    path('reservations/<int:reservation_pk>/generate_ticket/', views.generate_ticket, name='generate_ticket'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('flights/<int:flight_pk>/passengers/', views.passenger_list_by_flight, name='passenger_list_by_flight'),

    # Airplane URLs
    path('airplanes/', views.airplane_list, name='airplane_list'),
    path('airplanes/create/', views.airplane_create, name='airplane_create'),
    path('airplanes/update/<int:pk>/', views.airplane_update, name='airplane_update'),
    path('airplanes/delete/<int:pk>/', views.airplane_delete, name='airplane_delete'),

    # SeatLayout URLs
    path('seat_layouts/', views.seat_layout_list, name='seat_layout_list'),
    path('seat_layouts/create/', views.seat_layout_create, name='seat_layout_create'),
    path('seat_layouts/update/<int:pk>/', views.seat_layout_update, name='seat_layout_update'),
    path('seat_layouts/delete/<int:pk>/', views.seat_layout_delete, name='seat_layout_delete'),

    # SeatType URLs
    path('seat_types/', views.seat_type_list, name='seat_type_list'),
    path('seat_types/create/', views.seat_type_create, name='seat_type_create'),
    path('seat_types/update/<int:pk>/', views.seat_type_update, name='seat_type_update'),
    path('seat_types/delete/<int:pk>/', views.seat_type_delete, name='seat_type_delete'),

    # SeatLayoutPosition URLs
    path('seat_layout_positions/', views.seat_layout_position_list, name='seat_layout_position_list'),
    path('seat_layout_positions/create/', views.seat_layout_position_create, name='seat_layout_position_create'),
    path('seat_layout_positions/update/<int:pk>/', views.seat_layout_position_update, name='seat_layout_position_update'),
    path('seat_layout_positions/delete/<int:pk>/', views.seat_layout_position_delete, name='seat_layout_position_delete'),

    # API URLs
    path('api/', include(router.urls)),
]
