from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Trip
from vehicles.models import Vehicle
from drivers.models import Driver
from finance.models import FuelLog
from decimal import Decimal

def create_trip(source, destination, vehicle_id, driver_id, cargo_weight, planned_distance, revenue, user):
    with transaction.atomic():
        vehicle = Vehicle.objects.select_for_update().get(id=vehicle_id)
        driver = Driver.objects.select_for_update().get(id=driver_id)
        
        if cargo_weight > vehicle.max_load_capacity:
            raise ValidationError(f"Cargo weight ({cargo_weight}kg) exceeds vehicle capacity ({vehicle.max_load_capacity}kg).")
            
        if vehicle.status != 'Available':
            raise ValidationError(f"Vehicle is not Available. Current status: {vehicle.status}")
            
        if driver.status != 'Available' or driver.is_license_expired():
            raise ValidationError("Driver is not Available or license is expired.")
            
        trip = Trip.objects.create(
            source=source,
            destination=destination,
            vehicle=vehicle,
            driver=driver,
            cargo_weight=cargo_weight,
            planned_distance=planned_distance,
            revenue=revenue,
            created_by=user,
            status='Draft'
        )
        return trip

def dispatch_trip(trip):
    with transaction.atomic():
        # Lock rows
        trip = Trip.objects.select_for_update().get(id=trip.id)
        vehicle = Vehicle.objects.select_for_update().get(id=trip.vehicle_id)
        driver = Driver.objects.select_for_update().get(id=trip.driver_id)
        
        if trip.status != 'Draft':
            raise ValidationError(f"Only Draft trips can be dispatched. Current status: {trip.status}")
            
        if vehicle.status != 'Available':
            raise ValidationError("Vehicle is no longer available.")
            
        if driver.status != 'Available' or driver.is_license_expired():
            raise ValidationError("Driver is no longer available or license expired.")
            
        vehicle.status = 'On Trip'
        vehicle.save()
        
        driver.status = 'On Trip'
        driver.save()
        
        trip.status = 'Dispatched'
        trip.dispatched_at = timezone.now()
        trip.save()
        return trip

def complete_trip(trip, final_odometer, fuel_consumed):
    with transaction.atomic():
        trip = Trip.objects.select_for_update().get(id=trip.id)
        vehicle = Vehicle.objects.select_for_update().get(id=trip.vehicle_id)
        driver = Driver.objects.select_for_update().get(id=trip.driver_id)
        
        if trip.status != 'Dispatched':
            raise ValidationError(f"Only Dispatched trips can be completed. Current status: {trip.status}")
            
        previous_odometer = vehicle.odometer
        vehicle.status = 'Available'
        vehicle.odometer = final_odometer
        vehicle.save()
        
        driver.status = 'Available'
        driver.save()
        
        trip.status = 'Completed'
        trip.completed_at = timezone.now()
        trip.actual_distance = final_odometer - previous_odometer if final_odometer > previous_odometer else trip.planned_distance
        trip.fuel_consumed = fuel_consumed
        trip.save()
        
        # Automatically create Fuel Log
        if fuel_consumed and fuel_consumed > 0:
            cost = Decimal(fuel_consumed) * Decimal('90.00')  # Assuming 90 INR/L for automated entry
            FuelLog.objects.create(
                vehicle=vehicle,
                trip=trip,
                liters=fuel_consumed,
                cost=cost,
                date=timezone.now().date()
            )
            
        return trip

def cancel_trip(trip):
    with transaction.atomic():
        trip = Trip.objects.select_for_update().get(id=trip.id)
        vehicle = Vehicle.objects.select_for_update().get(id=trip.vehicle_id)
        driver = Driver.objects.select_for_update().get(id=trip.driver_id)
        
        if trip.status not in ['Draft', 'Dispatched']:
            raise ValidationError(f"Cannot cancel trip with status: {trip.status}")
            
        if trip.status == 'Dispatched':
            vehicle.status = 'Available'
            vehicle.save()
            driver.status = 'Available'
            driver.save()
            
        trip.status = 'Cancelled'
        trip.cancelled_at = timezone.now()
        trip.save()
        return trip
