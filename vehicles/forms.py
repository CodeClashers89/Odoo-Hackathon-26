from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['registration_number', 'name_model', 'vehicle_type', 'max_load_capacity', 'odometer', 'acquisition_cost', 'region', 'status']
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name_model': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.TextInput(attrs={'class': 'form-control'}),
            'max_load_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control'}),
            'acquisition_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
