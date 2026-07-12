from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Driver
from .forms import DriverForm
from accounts.decorators import role_required
from django.contrib import messages

@role_required('Fleet Manager', 'Safety Officer', 'Admin')
def driver_list(request):
    drivers = Driver.objects.all()
    return render(request, 'drivers/list.html', {'drivers': drivers})

@role_required('Admin')
def driver_create(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save(commit=False)
            
            # Create User account
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = driver.name.split(' ')[0] if ' ' in driver.name else driver.name
            user.last_name = driver.name.split(' ')[1] if ' ' in driver.name else ''
            user.save()
            
            # Set profile role to Driver
            profile = user.profile
            profile.role = 'Driver'
            profile.phone_number = driver.contact_number
            profile.save()
            
            # Associate User with Driver
            driver.user = user
            driver.save()
            
            messages.success(request, 'Driver and user account created successfully.')
            return redirect('drivers_list')
    else:
        form = DriverForm()
    return render(request, 'drivers/form.html', {'form': form, 'action': 'Create'})

@role_required('Admin')
def driver_edit(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            driver = form.save(commit=False)
            
            # Create or update associated user account
            if not driver.user:
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                user = User.objects.create_user(username=username, email=email, password=password)
                user.first_name = driver.name.split(' ')[0] if ' ' in driver.name else driver.name
                user.last_name = driver.name.split(' ')[1] if ' ' in driver.name else ''
                user.save()
                
                profile = user.profile
                profile.role = 'Driver'
                profile.phone_number = driver.contact_number
                profile.save()
                driver.user = user
            else:
                user = driver.user
                user.email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                if password:
                    user.set_password(password)
                user.save()
                
                profile = user.profile
                profile.phone_number = driver.contact_number
                profile.save()
                
            driver.save()
            messages.success(request, 'Driver and user account updated successfully.')
            return redirect('drivers_list')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'drivers/form.html', {'form': form, 'action': 'Edit'})

@role_required('Admin')
def driver_update_status(request, driver_id):
    if request.method == 'POST':
        driver = get_object_or_404(Driver, id=driver_id)
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Driver.STATUS_CHOICES]:
            driver.status = new_status
            driver.save()
            messages.success(request, f'Status for {driver.name} updated to {new_status}.')
    return redirect('drivers_list')

from django.core.management import call_command
from io import StringIO

@role_required('Admin')
def send_expiry_notifications(request):
    if request.method == 'POST':
        out = StringIO()
        try:
            call_command('send_notifications', stdout=out)
            output = out.getvalue().replace('\n', '<br>')
            messages.success(request, f"<strong>Execution Log:</strong><br>{output}")
        except Exception as e:
            messages.error(request, f"Error calling notification script: {str(e)}")
    return redirect('drivers_list')


@role_required('Fleet Manager', 'Safety Officer', 'Admin')
def driver_profile(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    trips = driver.trips.all().order_by('-created_at')
    
    # Calculate stats
    total_trips = trips.count()
    completed_trips = trips.filter(status='Completed')
    completed_trips_count = completed_trips.count()
    
    total_distance = sum(
        t.actual_distance if t.actual_distance is not None else t.planned_distance 
        for t in completed_trips
    )
    total_revenue = sum(t.revenue for t in completed_trips)
    
    infractions = driver.infractions.all().order_by('-date_reported')
    
    context = {
        'driver': driver,
        'trips': trips,
        'infractions': infractions,
        'stats': {
            'total_trips': total_trips,
            'completed_trips_count': completed_trips_count,
            'total_distance': total_distance,
            'total_revenue': total_revenue,
        }
    }
    return render(request, 'drivers/profile.html', context)

