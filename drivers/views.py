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
