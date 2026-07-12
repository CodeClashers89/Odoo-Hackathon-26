from django import forms
from .models import Trip
from vehicles.models import Vehicle
from drivers.models import Driver

class TripCreateForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['source', 'destination', 'vehicle', 'driver', 'cargo_weight', 'planned_distance', 'revenue']
        widgets = {
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'cargo_weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'planned_distance': forms.NumberInput(attrs={'class': 'form-control'}),
            'revenue': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available vehicles and drivers
        self.fields['vehicle'].queryset = Vehicle.objects.filter(status='Available')
        
        # Drivers must be available and not have expired licenses
        from datetime import date
        self.fields['driver'].queryset = Driver.objects.filter(
            status='Available',
            license_expiry_date__gte=date.today()
        )

class TripCompleteForm(forms.Form):
    final_odometer = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    fuel_consumed = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
