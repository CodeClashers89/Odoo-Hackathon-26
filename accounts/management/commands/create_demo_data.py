import datetime
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from accounts.models import Profile
from vehicles.models import Vehicle
from drivers.models import Driver
from trips.models import Trip
from maintenance.models import MaintenanceLog
from finance.models import FuelLog, Expense

class Command(BaseCommand):
    help = 'Creates a large set of fresh demo data for TransitOps'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old demo data...")
        Trip.objects.all().delete()
        MaintenanceLog.objects.all().delete()
        FuelLog.objects.all().delete()
        Expense.objects.all().delete()
        Vehicle.objects.all().delete()
        Driver.objects.all().delete()

        # Users
        roles = [
            ('admin', 'adminpass', 'Admin'),
            ('manager', 'managerpass', 'Fleet Manager'),
            ('driver', 'driverpass', 'Driver'),
            ('safety', 'safetypass', 'Safety Officer'),
            ('finance', 'financepass', 'Financial Analyst'),
        ]
        
        users_map = {}
        for username, password, role in roles:
            user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create_user(username=username, password=password)
                profile = user.profile
                profile.role = role
                profile.save()
            users_map[username] = user

        # Vehicles
        self.stdout.write("Creating Vehicles...")
        makes = ['Volvo FH16', 'Ford Transit', 'Mercedes Sprinter', 'Scania R500', 'MAN TGX', 'Tata Prima', 'Ashok Leyland', 'Eicher Pro']
        types = ['Truck', 'Van', 'Flatbed', 'Reefer']
        vehicles = []
        for i in range(1, 21):
            reg = f"GJ-03-{(random.randint(1000, 9999))}"
            model = random.choice(makes)
            vtype = random.choice(types)
            cap = random.choice([1500, 2000, 10000, 20000, 30000])
            odo = random.uniform(1000, 100000)
            cost = random.uniform(20000, 150000)
            status = random.choice(['Available', 'Available', 'Available', 'In Shop', 'On Trip'])
            
            v = Vehicle.objects.create(
                registration_number=reg,
                name_model=model,
                vehicle_type=vtype,
                max_load_capacity=cap,
                odometer=odo,
                acquisition_cost=cost,
                status=status,
                region=random.choice(['West Zone', 'North Zone', 'South Zone'])
            )
            vehicles.append(v)

        # Drivers
        self.stdout.write("Creating Drivers...")
        names = ['Alex Smith', 'Bob Jones', 'Charlie Brown', 'David Lee', 'Emma Watson', 'Frank Miller', 'George King', 'Harry Potter', 'Ian Wright', 'Jack Sparrow']
        drivers = []
        for i, name in enumerate(names):
            lic = f"DL-2026-{1000+i}"
            cat = random.choice(['Heavy', 'Light', 'Commercial'])
            # Most valid, some expired
            exp = timezone.now().date() + datetime.timedelta(days=random.randint(-100, 1000))
            status = random.choice(['Available', 'Available', 'Available', 'On Trip'])
            
            d = Driver.objects.create(
                name=name,
                license_number=lic,
                license_category=cat,
                license_expiry_date=exp,
                contact_number=f"555-01{i:02d}",
                status=status
            )
            drivers.append(d)

        # Trips
        self.stdout.write("Creating Trips...")
        locations = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Rajkot', 'Ahmedabad', 'Surat', 'Pune', 'Jaipur']
        trips = []
        for i in range(15):
            v = random.choice(vehicles)
            d = random.choice(drivers)
            src = random.choice(locations)
            dest = random.choice([loc for loc in locations if loc != src])
            status = random.choice(['Draft', 'Dispatched', 'Completed', 'Completed', 'Cancelled'])
            
            trip = Trip.objects.create(
                source=src,
                destination=dest,
                vehicle=v,
                driver=d,
                cargo_weight=Decimal(str(random.uniform(500, float(v.max_load_capacity)))),
                planned_distance=Decimal(str(random.uniform(50, 1000))),
                revenue=Decimal(str(random.uniform(5000, 50000))),
                created_by=users_map['manager'],
                status=status
            )
            
            if status in ['Dispatched', 'Completed']:
                trip.dispatched_at = timezone.now() - datetime.timedelta(days=random.randint(1, 5))
                v.status = 'On Trip' if status == 'Dispatched' else 'Available'
                d.status = 'On Trip' if status == 'Dispatched' else 'Available'
                
            if status == 'Completed':
                trip.completed_at = timezone.now()
                trip.actual_distance = trip.planned_distance * Decimal(str(random.uniform(0.9, 1.2)))
                trip.fuel_consumed = trip.actual_distance / Decimal(str(random.uniform(4.0, 8.0)))
                
                # Auto-generate FuelLog for completed trips
                FuelLog.objects.create(
                    vehicle=v,
                    trip=trip,
                    liters=trip.fuel_consumed,
                    cost=trip.fuel_consumed * Decimal('90.00'),
                    date=trip.completed_at.date()
                )
                
                # Add some random tolls or misc
                if random.choice([True, False]):
                    Expense.objects.create(
                        vehicle=v,
                        trip=trip,
                        expense_type='Toll',
                        amount=random.uniform(500, 2000),
                        date=trip.completed_at.date()
                    )
                    
            if status == 'Cancelled':
                trip.cancelled_at = timezone.now()
                
            trip.save()
            v.save()
            d.save()
            trips.append(trip)

        # Maintenance Logs
        self.stdout.write("Creating Maintenance Logs...")
        for i in range(8):
            v = random.choice(vehicles)
            status = random.choice(['Active', 'Closed'])
            m_type = random.choice(['Oil Change', 'Tire Replacement', 'Brake Inspection', 'Engine Overhaul'])
            log = MaintenanceLog.objects.create(
                vehicle=v,
                maintenance_type=m_type,
                description=f"Standard {m_type} procedure.",
                cost=random.uniform(1000, 25000),
                status=status
            )
            if status == 'Closed':
                log.closed_at = timezone.now()
                log.save()
            else:
                v.status = 'In Shop'
                v.save()

        self.stdout.write(self.style.SUCCESS('Successfully loaded a LOT of fresh demo data!'))
