from django.db import models
from vehicles.models import Vehicle

class MaintenanceLog(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    )

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    started_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.maintenance_type} for {self.vehicle.registration_number}"
