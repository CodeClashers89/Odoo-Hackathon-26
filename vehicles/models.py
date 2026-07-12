from django.db import models

class Vehicle(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('On Trip', 'On Trip'),
        ('In Shop', 'In Shop'),
        ('Retired', 'Retired'),
    )

    registration_number = models.CharField(max_length=50, unique=True, db_index=True)
    name_model = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=50)
    max_load_capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="in kg")
    odometer = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="in km")
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    region = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.registration_number} ({self.name_model})"
