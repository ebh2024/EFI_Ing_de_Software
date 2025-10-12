from django.test import TestCase
from ..forms import AirplaneForm, SeatLayoutForm, SeatTypeForm, SeatLayoutPositionForm
from ..models import Airplane, SeatLayout, SeatType, SeatLayoutPosition
import datetime

class AirplaneFormTest(TestCase):
    def setUp(self):
        self.seat_layout = SeatLayout.objects.create(
            layout_name="Test Layout",
            rows=10,
            columns=6
        )

    def test_airplane_form_valid(self):
        form_data = {
            'model_name': 'Boeing 737',
            'manufacturer': 'Boeing',
            'registration_number': 'N12345',
            'year_of_manufacture': 2010,
            'capacity': 150,
            'seat_layout': self.seat_layout.pk,
            'last_maintenance_date': '2023-01-01',
            'technical_notes': 'Routine check'
        }
        form = AirplaneForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_airplane_form_invalid_missing_model_name(self):
        form_data = {
            'manufacturer': 'Boeing',
            'registration_number': 'N12345',
            'year_of_manufacture': 2010,
            'capacity': 150,
            'seat_layout': self.seat_layout.pk,
            'last_maintenance_date': '2023-01-01',
            'technical_notes': 'Routine check'
        }
        form = AirplaneForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('model_name', form.errors)

    def test_airplane_form_invalid_duplicate_registration_number(self):
        Airplane.objects.create(
            model_name="Existing Plane",
            registration_number="N12345",
            capacity=100,
            seat_layout=self.seat_layout
        )
        form_data = {
            'model_name': 'Boeing 737',
            'manufacturer': 'Boeing',
            'registration_number': 'N12345',
            'year_of_manufacture': 2010,
            'capacity': 150,
            'seat_layout': self.seat_layout.pk,
            'last_maintenance_date': '2023-01-01',
            'technical_notes': 'Routine check'
        }
        form = AirplaneForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('registration_number', form.errors)

class SeatLayoutFormTest(TestCase):
    def test_seat_layout_form_valid(self):
        form_data = {
            'layout_name': 'Economy Layout',
            'rows': 30,
            'columns': 6
        }
        form = SeatLayoutForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_seat_layout_form_invalid_missing_name(self):
        form_data = {
            'rows': 30,
            'columns': 6
        }
        form = SeatLayoutForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('layout_name', form.errors)

    def test_seat_layout_form_invalid_duplicate_name(self):
        SeatLayout.objects.create(layout_name="Economy Layout", rows=10, columns=6)
        form_data = {
            'layout_name': 'Economy Layout',
            'rows': 20,
            'columns': 5
        }
        form = SeatLayoutForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('layout_name', form.errors)

class SeatTypeFormTest(TestCase):
    def test_seat_type_form_valid(self):
        form_data = {
            'name': 'Business Class',
            'code': 'BUS',
            'price_multiplier': 1.50
        }
        form = SeatTypeForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_seat_type_form_invalid_missing_name(self):
        form_data = {
            'code': 'BUS',
            'price_multiplier': 1.50
        }
        form = SeatTypeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_seat_type_form_invalid_duplicate_code(self):
        SeatType.objects.create(name="First Class", code="FST", price_multiplier=2.00)
        form_data = {
            'name': 'Premium Economy',
            'code': 'FST',
            'price_multiplier': 1.20
        }
        form = SeatTypeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

class SeatLayoutPositionFormTest(TestCase):
    def setUp(self):
        self.seat_layout = SeatLayout.objects.create(
            layout_name="Premium Layout",
            rows=5,
            columns=4
        )
        self.seat_type = SeatType.objects.create(
            name="Premium",
            code="PRE",
            price_multiplier=1.20
        )

    def test_seat_layout_position_form_valid(self):
        form_data = {
            'seat_layout': self.seat_layout.pk,
            'seat_type': self.seat_type.pk,
            'row': 1,
            'column': 'A'
        }
        form = SeatLayoutPositionForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_seat_layout_position_form_invalid_missing_seat_layout(self):
        form_data = {
            'seat_type': self.seat_type.pk,
            'row': 1,
            'column': 'A'
        }
        form = SeatLayoutPositionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('seat_layout', form.errors)

    def test_seat_layout_position_form_invalid_duplicate_position(self):
        SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout,
            seat_type=self.seat_type,
            row=1,
            column="A"
        )
        form_data = {
            'seat_layout': self.seat_layout.pk,
            'seat_type': self.seat_type.pk,
            'row': 1,
            'column': 'A'
        }
        form = SeatLayoutPositionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors) # unique_together constraint
