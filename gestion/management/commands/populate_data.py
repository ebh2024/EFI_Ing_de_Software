import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.models import Aircraft, Flight, Passenger, Seat, Booking
from django.utils import timezone
import random
import uuid

class Command(BaseCommand):
    help = 'Populates the database with sample data for users, flights, passengers, and bookings.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Clear existing data (optional, for fresh runs)
        Booking.objects.all().delete()
        Seat.objects.all().delete()
        Flight.objects.all().delete()
        Aircraft.objects.all().delete()
        Passenger.objects.all().delete()
        User.objects.filter(is_staff=False, is_superuser=False).delete() # Keep staff/superuser

        self.stdout.write(self.style.SUCCESS('Cleared existing data.'))

        # 1. Create Users and Passengers
        users_data = [
            {'username': 'user1@example.com', 'first_name': 'Alice', 'last_name': 'Smith', 'document_id': '12345678A', 'phone': '111-222-3333'},
            {'username': 'user2@example.com', 'first_name': 'Bob', 'last_name': 'Johnson', 'document_id': '87654321B', 'phone': '444-555-6666'},
            {'username': 'user3@example.com', 'first_name': 'Charlie', 'last_name': 'Brown', 'document_id': '11223344C', 'phone': '777-888-9999'},
            {'username': 'user4@example.com', 'first_name': 'Diana', 'last_name': 'Prince', 'document_id': '55667788D', 'phone': '123-456-7890'},
            {'username': 'user5@example.com', 'first_name': 'Eve', 'last_name': 'Adams', 'document_id': '99001122E', 'phone': '098-765-4321'},
            {'username': 'user6@example.com', 'first_name': 'Frank', 'last_name': 'White', 'document_id': '33445566F', 'phone': '234-567-8901'},
            {'username': 'user7@example.com', 'first_name': 'Grace', 'last_name': 'Green', 'document_id': '77889900G', 'phone': '345-678-9012'},
            {'username': 'user8@example.com', 'first_name': 'Heidi', 'last_name': 'Black', 'document_id': '10293847H', 'phone': '456-789-0123'},
            {'username': 'user9@example.com', 'first_name': 'Ivan', 'last_name': 'Grey', 'document_id': '65748392I', 'phone': '567-890-1234'},
            {'username': 'user10@example.com', 'first_name': 'Judy', 'last_name': 'Blue', 'document_id': '21324354J', 'phone': '678-901-2345'},
        ]

        passengers = []
        for data in users_data:
            user, created = User.objects.get_or_create(username=data['username'], defaults={'email': data['username']})
            if created:
                user.set_password('password123') # Set a default password for easy login
                user.save()
            passenger = Passenger.objects.create(
                user=user,
                first_name=data['first_name'],
                last_name=data['last_name'],
                document_id=data['document_id'],
                email=data['username'],
                phone=data['phone']
            )
            passengers.append(passenger)
        self.stdout.write(self.style.SUCCESS(f'Created {len(passengers)} users and passengers.'))

        # 2. Create Aircrafts
        aircrafts_data = [
            {'model': 'Boeing 737', 'capacity': 150, 'seat_layout': {'rows': [{'seats': [{'number': f'{r}{chr(65+c)}'} for c in range(6)]} for r in range(1, 26)]}},
            {'model': 'Airbus A320', 'capacity': 180, 'seat_layout': {'rows': [{'seats': [{'number': f'{r}{chr(65+c)}'} for c in range(6)]} for r in range(1, 31)]}},
            {'model': 'Embraer E190', 'capacity': 100, 'seat_layout': {'rows': [{'seats': [{'number': f'{r}{chr(65+c)}'} for c in range(4)]} for r in range(1, 26)]}},
        ]
        aircrafts = []
        for data in aircrafts_data:
            aircraft = Aircraft.objects.create(**data)
            aircrafts.append(aircraft)
        self.stdout.write(self.style.SUCCESS(f'Created {len(aircrafts)} aircrafts.'))

        # 3. Create Flights
        flights_data = [
            {'origin': 'Buenos Aires', 'destination': 'Cordoba', 'departure_offset_days': 1, 'duration_hours': 2, 'price': 50.00},
            {'origin': 'Cordoba', 'destination': 'Buenos Aires', 'departure_offset_days': 2, 'duration_hours': 2, 'price': 55.00},
            {'origin': 'Buenos Aires', 'destination': 'Mendoza', 'departure_offset_days': 3, 'duration_hours': 1.5, 'price': 70.00},
            {'origin': 'Mendoza', 'destination': 'Buenos Aires', 'departure_offset_days': 4, 'duration_hours': 1.5, 'price': 75.00},
            {'origin': 'Buenos Aires', 'destination': 'Bariloche', 'departure_offset_days': 5, 'duration_hours': 3, 'price': 120.00},
            {'origin': 'Bariloche', 'destination': 'Buenos Aires', 'departure_offset_days': 6, 'duration_hours': 3, 'price': 125.00},
            {'origin': 'Cordoba', 'destination': 'Salta', 'departure_offset_days': 7, 'duration_hours': 2.5, 'price': 90.00},
            {'origin': 'Salta', 'destination': 'Cordoba', 'departure_offset_days': 8, 'duration_hours': 2.5, 'price': 95.00},
            {'origin': 'Buenos Aires', 'destination': 'Iguazu', 'departure_offset_days': 9, 'duration_hours': 2, 'price': 110.00},
            {'origin': 'Iguazu', 'destination': 'Buenos Aires', 'departure_offset_days': 10, 'duration_hours': 2, 'price': 115.00},
        ]

        flights = []
        for i, data in enumerate(flights_data):
            departure_date = timezone.now() + datetime.timedelta(days=data['departure_offset_days'], hours=random.randint(8, 20))
            arrival_date = departure_date + datetime.timedelta(hours=data['duration_hours'])
            flight = Flight.objects.create(
                origin=data['origin'],
                destination=data['destination'],
                departure_date=departure_date,
                arrival_date=arrival_date,
                price=data['price'],
                aircraft=random.choice(aircrafts) # Assign a random aircraft
            )
            flights.append(flight)
        self.stdout.write(self.style.SUCCESS(f'Created {len(flights)} flights.'))

        # 4. Create Bookings (some pending, some completed)
        for i in range(10): # Create 10 bookings
            try:
                flight = random.choice(flights)
                passenger = random.choice(passengers)
                
                # Try to find an available seat for the chosen flight
                available_seats = Seat.objects.filter(flight=flight, status='available')
                if not available_seats.exists():
                    self.stdout.write(self.style.WARNING(f'No available seats for flight {flight}. Skipping booking.'))
                    continue
                
                seat = random.choice(available_seats)

                payment_status = random.choice(['pending', 'completed'])
                transaction_id = str(uuid.uuid4()) if payment_status == 'completed' else None
                payment_date = timezone.now() if payment_status == 'completed' else None

                booking = Booking.objects.create(
                    flight=flight,
                    passenger=passenger,
                    seat=seat,
                    payment_status=payment_status,
                    transaction_id=transaction_id,
                    payment_date=payment_date
                )

                if payment_status == 'completed':
                    seat.status = 'occupied'
                else:
                    seat.status = 'reserved' # Mark as reserved if payment is pending
                seat.save()
                self.stdout.write(self.style.SUCCESS(f'Created booking {booking.id} with status {payment_status}.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating booking: {e}'))

        self.stdout.write(self.style.SUCCESS('Data population complete!'))
