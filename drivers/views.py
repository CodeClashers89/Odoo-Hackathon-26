from django.shortcuts import render, get_object_or_404, redirect
from .models import Driver
from .forms import DriverForm
from accounts.decorators import role_required
from django.contrib import messages

@role_required('Fleet Manager', 'Safety Officer', 'Admin')
def driver_list(request):
    drivers = Driver.objects.all()
    return render(request, 'drivers/list.html', {'drivers': drivers})

@role_required('Safety Officer', 'Admin')
def driver_create(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver created successfully.')
            return redirect('drivers_list')
    else:
        form = DriverForm()
    return render(request, 'drivers/form.html', {'form': form, 'action': 'Create'})

@role_required('Safety Officer', 'Admin')
def driver_edit(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver updated successfully.')
            return redirect('drivers_list')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'drivers/form.html', {'form': form, 'action': 'Edit'})

@role_required('Safety Officer', 'Admin')
def driver_update_status(request, driver_id):
    if request.method == 'POST':
        driver = get_object_or_404(Driver, id=driver_id)
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Driver.STATUS_CHOICES]:
            driver.status = new_status
            driver.save()
            messages.success(request, f'Status for {driver.name} updated to {new_status}.')
    return redirect('drivers_list')
