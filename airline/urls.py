from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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
]
