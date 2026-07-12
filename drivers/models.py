from django.db import models
from datetime import date

class Driver(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('On Trip', 'On Trip'),
        ('Off Duty', 'Off Duty'),
        ('Suspended', 'Suspended'),
    )

    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    license_category = models.CharField(max_length=50)
    license_expiry_date = models.DateField()
    contact_number = models.CharField(max_length=20)
    safety_score = models.IntegerField(default=100, help_text="0-100")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_license_expired(self):
        return self.license_expiry_date < date.today()
