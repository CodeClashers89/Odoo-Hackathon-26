from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from accounts.decorators import role_required
from .models import MaintenanceLog
from .forms import MaintenanceForm
from .services import open_maintenance, close_maintenance

@role_required('Fleet Manager', 'Admin')
def maintenance_list(request):
    logs = MaintenanceLog.objects.all()
    return render(request, 'maintenance/list.html', {'logs': logs})

@role_required('Fleet Manager', 'Admin')
def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            try:
                open_maintenance(
                    vehicle_id=form.cleaned_data['vehicle'].id,
                    maintenance_type=form.cleaned_data['maintenance_type'],
                    description=form.cleaned_data['description'],
                    cost=form.cleaned_data['cost']
                )
                messages.success(request, 'Maintenance record created. Vehicle marked "In Shop".')
                return redirect('maintenance_list')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = MaintenanceForm()
    
    return render(request, 'maintenance/form.html', {'form': form})

@role_required('Fleet Manager', 'Admin')
def maintenance_close(request, log_id):
    log = get_object_or_404(MaintenanceLog, id=log_id)
    if request.method == 'POST':
        try:
            close_maintenance(log)
            messages.success(request, 'Maintenance closed. Vehicle is now Available.')
        except ValidationError as e:
            messages.error(request, str(e))
    return redirect('maintenance_list')
