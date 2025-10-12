from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import Airplane, SeatLayout, SeatType, SeatLayoutPosition
import uuid

class SeatLayoutModelTest(TestCase):
    def setUp(self):
        self.seat_layout = SeatLayout.objects.create(
            layout_name="Test Layout",
            rows=10,
            columns=6
        )

    def test_seat_layout_creation(self):
        self.assertEqual(self.seat_layout.layout_name, "Test Layout")
        self.assertEqual(self.seat_layout.rows, 10)
        self.assertEqual(self.seat_layout.columns, 6)
        self.assertEqual(str(self.seat_layout), "Test Layout")

    def test_unique_layout_name(self):
        with self.assertRaises(Exception): # IntegrityError or ValidationError
            SeatLayout.objects.create(
                layout_name="Test Layout",
                rows=5,
                columns=4
            )

class SeatTypeModelTest(TestCase):
    def setUp(self):
        self.seat_type = SeatType.objects.create(
            name="Economy",
            code="ECO",
            price_multiplier=1.00
        )

    def test_seat_type_creation(self):
        self.assertEqual(self.seat_type.name, "Economy")
        self.assertEqual(self.seat_type.code, "ECO")
        self.assertEqual(str(self.seat_type), "Economy")

    def test_unique_name_and_code(self):
        with self.assertRaises(Exception): # IntegrityError or ValidationError
            SeatType.objects.create(
                name="Economy",
                code="EC2",
                price_multiplier=1.10
            )
        with self.assertRaises(Exception): # IntegrityError or ValidationError
            SeatType.objects.create(
                name="Economy Plus",
                code="ECO",
                price_multiplier=1.10
            )

class AirplaneModelTest(TestCase):
    def setUp(self):
        self.seat_layout = SeatLayout.objects.create(
            layout_name="Business Layout",
            rows=5,
            columns=4
        )
        self.airplane = Airplane.objects.create(
            model_name="Boeing 747",
            manufacturer="Boeing",
            registration_number="RA-12345",
            year_of_manufacture=2000,
            capacity=300,
            seat_layout=self.seat_layout,
            last_maintenance_date="2023-01-01",
            technical_notes="Some notes"
        )

    def test_airplane_creation(self):
        self.assertEqual(self.airplane.model_name, "Boeing 747")
        self.assertEqual(self.airplane.registration_number, "RA-12345")
        self.assertEqual(self.airplane.capacity, 300)
        self.assertEqual(self.airplane.seat_layout, self.seat_layout)
        self.assertEqual(str(self.airplane), "Boeing 747 (RA-12345)")

    def test_unique_registration_number(self):
        with self.assertRaises(Exception): # IntegrityError or ValidationError
            Airplane.objects.create(
                model_name="Airbus A320",
                registration_number="RA-12345",
                capacity=150
            )

    def test_default_registration_number(self):
        airplane_no_reg = Airplane.objects.create(
            model_name="Default Plane",
            capacity=100
        )
        self.assertIsNotNone(airplane_no_reg.registration_number)
        self.assertNotEqual(airplane_no_reg.registration_number, "")

class SeatLayoutPositionModelTest(TestCase):
    def setUp(self):
        self.seat_layout = SeatLayout.objects.create(
            layout_name="First Class Layout",
            rows=2,
            columns=2
        )
        self.seat_type = SeatType.objects.create(
            name="First Class",
            code="FST",
            price_multiplier=2.00
        )
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout,
            seat_type=self.seat_type,
            row=1,
            column="A"
        )

    def test_seat_layout_position_creation(self):
        self.assertEqual(self.seat_layout_position.seat_layout, self.seat_layout)
        self.assertEqual(self.seat_layout_position.seat_type, self.seat_type)
        self.assertEqual(self.seat_layout_position.row, 1)
        self.assertEqual(self.seat_layout_position.column, "A")
        self.assertEqual(str(self.seat_layout_position), "First Class Layout - Row 1, Col A (FST)")

    def test_unique_seat_layout_position(self):
        with self.assertRaises(Exception): # IntegrityError or ValidationError
            SeatLayoutPosition.objects.create(
                seat_layout=self.seat_layout,
                seat_type=self.seat_type,
                row=1,
                column="A"
            )
