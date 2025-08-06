from django.urls import path
from . import views

urlpatterns = [
    path('', views.flight_list, name='flight_list'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('book/<int:seat_id>/', views.book_seat, name='book_seat'),
    path('ticket/<int:booking_id>/', views.ticket, name='ticket'),
    path('report/flight/<int:flight_id>/', views.passenger_report_by_flight, name='passenger_report_by_flight'),
    path('passenger/create/', views.create_passenger, name='create_passenger'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark_read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('payment/<int:booking_id>/', views.process_payment, name='process_payment'),
]
