from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.contrib.auth import views as auth_views
from airline import views, crud_views, api_views
from rest_framework.routers import DefaultRouter

class URLTests(SimpleTestCase):

    def test_home_url_resolves(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, views.home)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, auth_views.LoginView)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func.view_class, auth_views.LogoutView)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, views.register)

    # Flight URLs
    def test_flight_list_url_resolves(self):
        url = reverse('flight_list')
        self.assertEqual(resolve(url).func, crud_views.flight_list)

    def test_flight_create_url_resolves(self):
        url = reverse('flight_create')
        self.assertEqual(resolve(url).func, crud_views.flight_create)

    def test_flight_update_url_resolves(self):
        url = reverse('flight_update', args=[1])
        self.assertEqual(resolve(url).func, crud_views.flight_update)

    def test_flight_delete_url_resolves(self):
        url = reverse('flight_delete', args=[1])
        self.assertEqual(resolve(url).func, crud_views.flight_delete)

    # Passenger URLs
    def test_passenger_list_url_resolves(self):
        url = reverse('passenger_list')
        self.assertEqual(resolve(url).func, crud_views.passenger_list)

    def test_passenger_create_url_resolves(self):
        url = reverse('passenger_create')
        self.assertEqual(resolve(url).func, crud_views.passenger_create)

    def test_passenger_update_url_resolves(self):
        url = reverse('passenger_update', args=[1])
        self.assertEqual(resolve(url).func, crud_views.passenger_update)

    def test_passenger_delete_url_resolves(self):
        url = reverse('passenger_delete', args=[1])
        self.assertEqual(resolve(url).func, crud_views.passenger_delete)

    def test_passenger_flight_history_url_resolves(self):
        url = reverse('passenger_flight_history', args=[1])
        self.assertEqual(resolve(url).func, views.passenger_flight_history)

    # Reservation System URLs
    def test_flight_detail_with_seats_url_resolves(self):
        url = reverse('flight_detail_with_seats', args=[1])
        self.assertEqual(resolve(url).func, views.flight_detail_with_seats)

    def test_reserve_seat_url_resolves(self):
        url = reverse('reserve_seat', args=[1, 1])
        self.assertEqual(resolve(url).func, views.reserve_seat)

    def test_reservation_list_url_resolves(self):
        url = reverse('reservation_list')
        self.assertEqual(resolve(url).func, views.reservation_list)

    def test_reservation_detail_url_resolves(self):
        url = reverse('reservation_detail', args=[1])
        self.assertEqual(resolve(url).func, views.reservation_detail)

    def test_reservation_update_status_url_resolves(self):
        url = reverse('reservation_update_status', args=[1, 'CONFIRMED'])
        self.assertEqual(resolve(url).func, views.reservation_update_status)

    def test_generate_ticket_url_resolves(self):
        url = reverse('generate_ticket', args=[1])
        self.assertEqual(resolve(url).func, views.generate_ticket)

    def test_ticket_detail_url_resolves(self):
        url = reverse('ticket_detail', args=[1])
        self.assertEqual(resolve(url).func, views.ticket_detail)

    def test_passenger_list_by_flight_url_resolves(self):
        url = reverse('passenger_list_by_flight', args=[1])
        self.assertEqual(resolve(url).func, views.passenger_list_by_flight)

    # Airplane URLs
    def test_airplane_list_url_resolves(self):
        url = reverse('airplane_list')
        self.assertEqual(resolve(url).func, crud_views.airplane_list)

    def test_airplane_create_url_resolves(self):
        url = reverse('airplane_create')
        self.assertEqual(resolve(url).func, crud_views.airplane_create)

    def test_airplane_update_url_resolves(self):
        url = reverse('airplane_update', args=[1])
        self.assertEqual(resolve(url).func, crud_views.airplane_update)

    def test_airplane_delete_url_resolves(self):
        url = reverse('airplane_delete', args=[1])
        self.assertEqual(resolve(url).func, crud_views.airplane_delete)

    # SeatLayout URLs
    def test_seat_layout_list_url_resolves(self):
        url = reverse('seat_layout_list')
        self.assertEqual(resolve(url).func, crud_views.seat_layout_list)

    def test_seat_layout_create_url_resolves(self):
        url = reverse('seat_layout_create')
        self.assertEqual(resolve(url).func, crud_views.seat_layout_create)

    def test_seat_layout_update_url_resolves(self):
        url = reverse('seat_layout_update', args=[1])
        self.assertEqual(resolve(url).func, crud_views.seat_layout_update)

    def test_seat_layout_delete_url_resolves(self):
        url = reverse('seat_layout_delete', args=[1])
        self.assertEqual(resolve(url).func, crud_views.seat_layout_delete)

    # SeatType URLs
    def test_seat_type_list_url_resolves(self):
        url = reverse('seat_type_list')
        self.assertEqual(resolve(url).func, crud_views.seat_type_list)

    def test_seat_type_create_url_resolves(self):
        url = reverse('seat_type_create')
        self.assertEqual(resolve(url).func, crud_views.seat_type_create)

    def test_seat_type_update_url_resolves(self):
        url = reverse('seat_type_update', args=[1])
        self.assertEqual(resolve(url).func, crud_views.seat_type_update)

    def test_seat_type_delete_url_resolves(self):
        url = reverse('seat_type_delete', args=[1])
        self.assertEqual(resolve(url).func, crud_views.seat_type_delete)

    # SeatLayoutPosition URLs
    def test_seat_layout_position_list_url_resolves(self):
        url = reverse('seat_layout_position_list')
        self.assertEqual(resolve(url).func, crud_views.seat_layout_position_list)

    def test_seat_layout_position_create_url_resolves(self):
        url = reverse('seat_layout_position_create')
        self.assertEqual(resolve(url).func, crud_views.seat_layout_position_create)

    def test_seat_layout_position_update_url_resolves(self):
        url = reverse('seat_layout_position_update', args=[1])
        self.assertEqual(resolve(url).func, crud_views.seat_layout_position_update)

    def test_seat_layout_position_delete_url_resolves(self):
        url = reverse('seat_layout_position_delete', args=[1])
        self.assertEqual(resolve(url).func, crud_views.seat_layout_position_delete)

    # API URLs
    def test_api_airplanes_list_url_resolves(self):
        url = reverse('airplane-list')
        self.assertEqual(resolve(url).func.cls, api_views.AirplaneViewSet)

    def test_api_flights_list_url_resolves(self):
        url = reverse('flight-list')
        self.assertEqual(resolve(url).func.cls, api_views.FlightViewSet)

    def test_api_passengers_list_url_resolves(self):
        url = reverse('passenger-list')
        self.assertEqual(resolve(url).func.cls, api_views.PassengerViewSet)

    def test_api_reservations_list_url_resolves(self):
        url = reverse('reservation-list')
        self.assertEqual(resolve(url).func.cls, api_views.ReservationViewSet)

    def test_api_seat_layouts_list_url_resolves(self):
        url = reverse('seatlayout-list')
        self.assertEqual(resolve(url).func.cls, api_views.SeatLayoutViewSet)

    def test_api_seat_types_list_url_resolves(self):
        url = reverse('seattype-list')
        self.assertEqual(resolve(url).func.cls, api_views.SeatTypeViewSet)

    def test_api_seat_layout_positions_list_url_resolves(self):
        url = reverse('seatlayoutposition-list')
        self.assertEqual(resolve(url).func.cls, api_views.SeatLayoutPositionViewSet)

    def test_api_flight_history_list_url_resolves(self):
        url = reverse('flighthistory-list')
        self.assertEqual(resolve(url).func.cls, api_views.FlightHistoryViewSet)

    def test_api_tickets_list_url_resolves(self):
        url = reverse('ticket-list')
        self.assertEqual(resolve(url).func.cls, api_views.TicketViewSet)
