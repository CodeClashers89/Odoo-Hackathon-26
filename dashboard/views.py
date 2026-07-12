from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from vehicles.models import Vehicle
from drivers.models import Driver
from trips.models import Trip

@login_required
def index(request):
    # Filter controls for dashboard (optional advanced feature)
    vehicle_type = request.GET.get('vehicle_type')
    region = request.GET.get('region')
    
    vehicles = Vehicle.objects.all()
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)
    if region:
        vehicles = vehicles.filter(region=region)
        
    active_vehicles = vehicles.filter(status='On Trip').count()
    available_vehicles = vehicles.filter(status='Available').count()
    maintenance_vehicles = vehicles.filter(status='In Shop').count()
    
    active_trips = Trip.objects.filter(status='Dispatched').count()
    pending_trips = Trip.objects.filter(status='Draft').count()
    drivers_on_duty = Driver.objects.filter(status='On Trip').count()
    
    total_active_fleet = vehicles.exclude(status='Retired').count()
    fleet_utilization = 0
    if total_active_fleet > 0:
        fleet_utilization = (active_vehicles / total_active_fleet) * 100
        
    recent_revenue_trips = Trip.objects.exclude(revenue__isnull=True).order_by('-created_at')[:15]
    recent_revenue_trips = list(recent_revenue_trips)[::-1]
    revenue_labels = [f"Trip {t.id}" for t in recent_revenue_trips]
    revenue_data = [float(t.revenue) for t in recent_revenue_trips]
    
    total_revenue_aggr = Trip.objects.aggregate(total=Sum('revenue'))
    total_revenue = float(total_revenue_aggr['total'] or 0)
        
    context = {
        'active_vehicles': active_vehicles,
        'available_vehicles': available_vehicles,
        'maintenance_vehicles': maintenance_vehicles,
        'active_trips': active_trips,
        'pending_trips': pending_trips,
        'drivers_on_duty': drivers_on_duty,
        'fleet_utilization': round(fleet_utilization, 1),
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard/index.html', context)
