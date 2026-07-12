from django import forms
from .models import MaintenanceLog
from vehicles.models import Vehicle

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        fields = ['vehicle', 'maintenance_type', 'description', 'cost']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow maintenance on vehicles that are not Retired
        self.fields['vehicle'].queryset = Vehicle.objects.exclude(status='Retired')
