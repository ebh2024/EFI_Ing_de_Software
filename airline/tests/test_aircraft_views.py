from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Airplane, SeatLayout, SeatType, SeatLayoutPosition
from ..forms import AirplaneForm, SeatLayoutForm, SeatTypeForm, SeatLayoutPositionForm
import datetime

class AircraftViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.seat_layout = SeatLayout.objects.create(
            layout_name="Test Layout",
            rows=10,
            columns=6
        )
        self.seat_type = SeatType.objects.create(
            name="Economy",
            code="ECO",
            price_multiplier=1.00
        )
        self.airplane = Airplane.objects.create(
            model_name="Boeing 747",
            registration_number="RA-12345",
            capacity=300,
            seat_layout=self.seat_layout
        )
        self.seat_layout_position = SeatLayoutPosition.objects.create(
            seat_layout=self.seat_layout,
            seat_type=self.seat_type,
            row=1,
            column="A"
        )

    # --- Airplane Views Tests ---
    def test_airplane_list_view(self):
        response = self.client.get(reverse('airplane_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/airplane_list.html')
        self.assertContains(response, self.airplane.model_name)

    def test_airplane_create_view_get(self):
        response = self.client.get(reverse('airplane_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/airplane_form.html')
        self.assertIsInstance(response.context['form'], AirplaneForm)

    def test_airplane_create_view_post_valid(self):
        form_data = {
            'model_name': 'Airbus A320',
            'manufacturer': 'Airbus',
            'registration_number': 'F-ABCD',
            'year_of_manufacture': 2015,
            'capacity': 180,
            'seat_layout': self.seat_layout.pk,
            'last_maintenance_date': '2023-05-01',
            'technical_notes': 'New engine'
        }
        response = self.client.post(reverse('airplane_create'), data=form_data)
        self.assertEqual(response.status_code, 302) # Redirect to list view
        self.assertTrue(Airplane.objects.filter(model_name='Airbus A320').exists())

    def test_airplane_create_view_post_invalid(self):
        form_data = {
            'model_name': '', # Invalid data
            'registration_number': 'F-ABCD',
            'capacity': 180,
            'seat_layout': self.seat_layout.pk
        }
        response = self.client.post(reverse('airplane_create'), data=form_data)
        self.assertEqual(response.status_code, 200) # Stays on form page
        self.assertFormError(response.context['form'], 'model_name', 'This field is required.')

    def test_airplane_update_view_get(self):
        response = self.client.get(reverse('airplane_update', args=[self.airplane.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/airplane_form.html')
        self.assertIsInstance(response.context['form'], AirplaneForm)
        self.assertEqual(response.context['form'].instance, self.airplane)

    def test_airplane_update_view_post_valid(self):
        form_data = {
            'model_name': 'Boeing 747 Updated',
            'manufacturer': 'Boeing',
            'registration_number': self.airplane.registration_number, # Keep unique
            'year_of_manufacture': 2000,
            'capacity': 350,
            'seat_layout': self.seat_layout.pk,
            'last_maintenance_date': '2023-01-01',
            'technical_notes': 'Some updated notes'
        }
        response = self.client.post(reverse('airplane_update', args=[self.airplane.pk]), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.airplane.refresh_from_db()
        self.assertEqual(self.airplane.model_name, 'Boeing 747 Updated')

    def test_airplane_delete_view_get(self):
        response = self.client.get(reverse('airplane_delete', args=[self.airplane.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/airplane_confirm_delete.html')
        self.assertEqual(response.context['airplane'], self.airplane)

    def test_airplane_delete_view_post(self):
        response = self.client.post(reverse('airplane_delete', args=[self.airplane.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Airplane.objects.filter(pk=self.airplane.pk).exists())

    # --- SeatLayout Views Tests ---
    def test_seat_layout_list_view(self):
        response = self.client.get(reverse('seat_layout_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_layout_list.html')
        self.assertContains(response, self.seat_layout.layout_name)

    def test_seat_layout_create_view_get(self):
        response = self.client.get(reverse('seat_layout_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_layout_form.html')
        self.assertIsInstance(response.context['form'], SeatLayoutForm)

    def test_seat_layout_create_view_post_valid(self):
        form_data = {
            'layout_name': 'New Layout',
            'rows': 5,
            'columns': 3
        }
        response = self.client.post(reverse('seat_layout_create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SeatLayout.objects.filter(layout_name='New Layout').exists())

    def test_seat_layout_update_view_get(self):
        response = self.client.get(reverse('seat_layout_update', args=[self.seat_layout.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_layout_form.html')
        self.assertIsInstance(response.context['form'], SeatLayoutForm)
        self.assertEqual(response.context['form'].instance, self.seat_layout)

    def test_seat_layout_update_view_post_valid(self):
        form_data = {
            'layout_name': 'Updated Layout',
            'rows': 12,
            'columns': 7
        }
        response = self.client.post(reverse('seat_layout_update', args=[self.seat_layout.pk]), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.seat_layout.refresh_from_db()
        self.assertEqual(self.seat_layout.layout_name, 'Updated Layout')

    def test_seat_layout_delete_view_post(self):
        response = self.client.post(reverse('seat_layout_delete', args=[self.seat_layout.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SeatLayout.objects.filter(pk=self.seat_layout.pk).exists())

    # --- SeatType Views Tests ---
    def test_seat_type_list_view(self):
        response = self.client.get(reverse('seat_type_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_type_list.html')
        self.assertContains(response, self.seat_type.name)

    def test_seat_type_create_view_get(self):
        response = self.client.get(reverse('seat_type_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_type_form.html')
        self.assertIsInstance(response.context['form'], SeatTypeForm)

    def test_seat_type_create_view_post_valid(self):
        form_data = {
            'name': 'Business Class',
            'code': 'BUS',
            'price_multiplier': 1.50
        }
        response = self.client.post(reverse('seat_type_create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SeatType.objects.filter(name='Business Class').exists())

    def test_seat_type_update_view_get(self):
        response = self.client.get(reverse('seat_type_update', args=[self.seat_type.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_type_form.html')
        self.assertIsInstance(response.context['form'], SeatTypeForm)
        self.assertEqual(response.context['form'].instance, self.seat_type)

    def test_seat_type_update_view_post_valid(self):
        form_data = {
            'name': 'Economy Plus',
            'code': self.seat_type.code, # Keep unique
            'price_multiplier': 1.20
        }
        response = self.client.post(reverse('seat_type_update', args=[self.seat_type.pk]), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.seat_type.refresh_from_db()
        self.assertEqual(self.seat_type.name, 'Economy Plus')

    def test_seat_type_delete_view_post(self):
        response = self.client.post(reverse('seat_type_delete', args=[self.seat_type.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SeatType.objects.filter(pk=self.seat_type.pk).exists())

    # --- SeatLayoutPosition Views Tests ---
    def test_seat_layout_position_list_view(self):
        response = self.client.get(reverse('seat_layout_position_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_layout_position_list.html')
        self.assertContains(response, self.seat_layout_position.seat_layout.layout_name)
        self.assertContains(response, self.seat_layout_position.seat_type.name)
        self.assertContains(response, str(self.seat_layout_position.row))
        self.assertContains(response, self.seat_layout_position.column)

    def test_seat_layout_position_create_view_get(self):
        response = self.client.get(reverse('seat_layout_position_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_layout_position_form.html')
        self.assertIsInstance(response.context['form'], SeatLayoutPositionForm)

    def test_seat_layout_position_create_view_post_valid(self):
        form_data = {
            'seat_layout': self.seat_layout.pk,
            'seat_type': self.seat_type.pk,
            'row': 2,
            'column': 'B'
        }
        response = self.client.post(reverse('seat_layout_position_create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SeatLayoutPosition.objects.filter(row=2, column='B').exists())

    def test_seat_layout_position_update_view_get(self):
        response = self.client.get(reverse('seat_layout_position_update', args=[self.seat_layout_position.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'airline/seat_layout_position_form.html')
        self.assertIsInstance(response.context['form'], SeatLayoutPositionForm)
        self.assertEqual(response.context['form'].instance, self.seat_layout_position)

    def test_seat_layout_position_update_view_post_valid(self):
        form_data = {
            'seat_layout': self.seat_layout.pk,
            'seat_type': self.seat_type.pk,
            'row': 1,
            'column': 'C' # Update column
        }
        response = self.client.post(reverse('seat_layout_position_update', args=[self.seat_layout_position.pk]), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.seat_layout_position.refresh_from_db()
        self.assertEqual(self.seat_layout_position.column, 'C')

    def test_seat_layout_position_delete_view_post(self):
        response = self.client.post(reverse('seat_layout_position_delete', args=[self.seat_layout_position.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SeatLayoutPosition.objects.filter(pk=self.seat_layout_position.pk).exists())
