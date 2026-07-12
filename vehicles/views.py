from django.shortcuts import render, get_object_or_404, redirect
from .models import Vehicle
from .forms import VehicleForm
from accounts.decorators import role_required
from django.contrib import messages

@role_required('Fleet Manager', 'Safety Officer', 'Admin')
def vehicle_list(request):
    status_filter = request.GET.get('status')
    vehicles = Vehicle.objects.all()
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    
    return render(request, 'vehicles/list.html', {'vehicles': vehicles, 'status_filter': status_filter})

@role_required('Fleet Manager', 'Admin')
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle created successfully.')
            return redirect('vehicles_list')
    else:
        form = VehicleForm()
    return render(request, 'vehicles/form.html', {'form': form, 'action': 'Create'})
