from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from accounts.decorators import role_required
from .models import Trip
from .forms import TripCreateForm, TripCompleteForm
from .services import create_trip, dispatch_trip, complete_trip, cancel_trip

@role_required('Fleet Manager', 'Safety Officer', 'Driver', 'Admin')
def trip_list(request):
    trips = Trip.objects.all()
    
    # Drivers only see their own trips
    if hasattr(request.user, 'profile') and request.user.profile.role == 'Driver':
        trips = trips.filter(driver__name=request.user.get_full_name() or request.user.username)
        
    return render(request, 'trips/list.html', {'trips': trips})

@role_required('Fleet Manager', 'Driver', 'Admin')
def trip_create(request):
    if request.method == 'POST':
        form = TripCreateForm(request.POST)
        if form.is_valid():
            try:
                trip = create_trip(
                    source=form.cleaned_data['source'],
                    destination=form.cleaned_data['destination'],
                    vehicle_id=form.cleaned_data['vehicle'].id,
                    driver_id=form.cleaned_data['driver'].id,
                    cargo_weight=form.cleaned_data['cargo_weight'],
                    planned_distance=form.cleaned_data['planned_distance'],
                    revenue=form.cleaned_data['revenue'],
                    user=request.user
                )
                messages.success(request, 'Trip created successfully (Draft).')
                return redirect('trips_list')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = TripCreateForm()
    
    return render(request, 'trips/form.html', {'form': form})

@role_required('Fleet Manager', 'Safety Officer', 'Driver', 'Admin')
def trip_detail(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    
    # Check driver access
    if hasattr(request.user, 'profile') and request.user.profile.role == 'Driver':
        if trip.driver.name != (request.user.get_full_name() or request.user.username):
            messages.error(request, 'You do not have permission to view this trip.')
            return redirect('trips_list')
            
    return render(request, 'trips/detail.html', {'trip': trip})

@role_required('Fleet Manager', 'Driver', 'Admin')
def trip_dispatch(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == 'POST':
        try:
            dispatch_trip(trip)
            messages.success(request, 'Trip dispatched successfully.')
        except ValidationError as e:
            messages.error(request, str(e))
    return redirect('trips_list')

@role_required('Fleet Manager', 'Driver', 'Admin')
def trip_complete(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == 'POST':
        form = TripCompleteForm(request.POST)
        if form.is_valid():
            try:
                complete_trip(
                    trip,
                    form.cleaned_data['final_odometer'],
                    form.cleaned_data['fuel_consumed']
                )
                messages.success(request, 'Trip completed successfully.')
                return redirect('trips_list')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = TripCompleteForm(initial={'final_odometer': trip.vehicle.odometer})
    
    return render(request, 'trips/complete_form.html', {'form': form, 'trip': trip})

@role_required('Fleet Manager', 'Driver', 'Admin')
def trip_cancel(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == 'POST':
        try:
            cancel_trip(trip)
            messages.success(request, 'Trip cancelled.')
        except ValidationError as e:
            messages.error(request, str(e))
    return redirect('trips_list')
