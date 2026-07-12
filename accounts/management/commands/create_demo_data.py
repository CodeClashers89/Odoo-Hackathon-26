import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from vehicles.models import Vehicle
from drivers.models import Driver

class Command(BaseCommand):
    help = 'Creates demo data for TransitOps (Users, Vehicles, Drivers)'

    def handle(self, *args, **kwargs):
        # Create users
        roles = [
            ('admin', 'adminpass', 'Admin'),
            ('manager', 'managerpass', 'Fleet Manager'),
            ('driver', 'driverpass', 'Driver'),
            ('safety', 'safetypass', 'Safety Officer'),
            ('finance', 'financepass', 'Financial Analyst'),
        ]

        for username, password, role in roles:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                profile = user.profile
                profile.role = role
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'Created user {username} with role {role}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))

        # Create Vehicles
        vehicles_data = [
            ('TRK-001', 'Volvo FH16', 'Truck', 20000.0, 15000.5, 120000.0, 'Available'),
            ('VAN-001', 'Ford Transit', 'Van', 1500.0, 50000.0, 35000.0, 'Available'),
            ('VAN-002', 'Mercedes Sprinter', 'Van', 1800.0, 12000.0, 40000.0, 'In Shop'),
        ]

        for reg, model, vtype, cap, odo, cost, status in vehicles_data:
            obj, created = Vehicle.objects.get_or_create(
                registration_number=reg,
                defaults={
                    'name_model': model,
                    'vehicle_type': vtype,
                    'max_load_capacity': cap,
                    'odometer': odo,
                    'acquisition_cost': cost,
                    'status': status,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created vehicle {reg}'))

        # Create Drivers
        drivers_data = [
            ('Alex Smith', 'DL-1001', 'Heavy', datetime.date(2027, 5, 10), '555-0101', 'Available'),
            ('Bob Jones', 'DL-1002', 'Light', datetime.date(2028, 1, 15), '555-0102', 'Available'),
            ('Charlie Brown', 'DL-1003', 'Heavy', datetime.date(2025, 6, 20), '555-0103', 'Suspended'), # Expired
        ]

        for name, lic, cat, exp, contact, status in drivers_data:
            obj, created = Driver.objects.get_or_create(
                license_number=lic,
                defaults={
                    'name': name,
                    'license_category': cat,
                    'license_expiry_date': exp,
                    'contact_number': contact,
                    'status': status,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created driver {name}'))

        self.stdout.write(self.style.SUCCESS('Successfully created demo data'))
