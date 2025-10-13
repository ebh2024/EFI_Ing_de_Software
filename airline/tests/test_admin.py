from django.test import TestCase
from django.contrib import admin
from django.apps import apps
from ..models import Airplane, Flight, SeatLayout, SeatType, SeatLayoutPosition, Passenger, FlightHistory, Seat, Reservation, Ticket, UserProfile

class AdminTest(TestCase):
    def test_admin_models_registered(self):
        """
        Test that all models are registered with the admin site.
        """
        registered_models = admin.site._registry.keys()
        expected_models = [
            Airplane, Flight, SeatLayout, SeatType, SeatLayoutPosition,
            Passenger, FlightHistory, Seat, Reservation, Ticket, UserProfile
        ]

        for model in expected_models:
            self.assertIn(model, registered_models, f"Model {model.__name__} not registered with admin site.")

    def test_admin_model_has_admin_class(self):
        """
        Test that each registered model has a corresponding ModelAdmin class,
        or uses the default ModelAdmin.
        """
        for model, model_admin in admin.site._registry.items():
            # Check if a custom ModelAdmin is used or if it's the default one
            self.assertTrue(issubclass(model_admin.__class__, admin.ModelAdmin))

    def test_admin_site_has_all_models_from_app(self):
        """
        Test that all models defined in the 'airline' app are registered with the admin site.
        This is a more comprehensive check.
        """
        airline_app_config = apps.get_app_config('airline')
        all_airline_models = airline_app_config.get_models()
        registered_models = admin.site._registry.keys()

        for model in all_airline_models:
            self.assertIn(model, registered_models, f"Model {model.__name__} from app 'airline' not registered with admin site.")
