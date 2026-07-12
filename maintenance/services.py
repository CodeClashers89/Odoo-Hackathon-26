from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import MaintenanceLog
from vehicles.models import Vehicle

def open_maintenance(vehicle_id, maintenance_type, description, cost):
    with transaction.atomic():
        vehicle = Vehicle.objects.select_for_update().get(id=vehicle_id)
        
        if vehicle.status == 'Retired':
            raise ValidationError("Cannot perform maintenance on a Retired vehicle.")
            
        # Creating active maintenance automatically sets vehicle to 'In Shop'
        log = MaintenanceLog.objects.create(
            vehicle=vehicle,
            maintenance_type=maintenance_type,
            description=description,
            cost=cost,
            status='Active'
        )
        
        vehicle.status = 'In Shop'
        vehicle.save()
        
        return log

def close_maintenance(log):
    with transaction.atomic():
        log = MaintenanceLog.objects.select_for_update().get(id=log.id)
        vehicle = Vehicle.objects.select_for_update().get(id=log.vehicle_id)
        
        if log.status == 'Closed':
            raise ValidationError("Maintenance log is already closed.")
            
        log.status = 'Closed'
        log.closed_at = timezone.now()
        log.save()
        
        # Restore vehicle status to Available, unless it was separately marked Retired
        if vehicle.status != 'Retired':
            vehicle.status = 'Available'
            vehicle.save()
            
        return log
