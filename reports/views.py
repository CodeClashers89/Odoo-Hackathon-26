from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from vehicles.models import Vehicle
from trips.models import Trip
from maintenance.models import MaintenanceLog
from finance.models import FuelLog
from django.db.models import Sum, F
import csv

@role_required('Financial Analyst', 'Fleet Manager', 'Admin')
def reports_view(request):
    return render(request, 'reports/index.html')

@role_required('Financial Analyst', 'Fleet Manager', 'Admin')
def reports_data(request):
    # 1. Operational Cost per Vehicle
    cost_data = []
    vehicles = Vehicle.objects.exclude(status='Retired')
    for v in vehicles:
        fuel_cost = FuelLog.objects.filter(vehicle=v).aggregate(Sum('cost'))['cost__sum'] or 0
        maint_cost = MaintenanceLog.objects.filter(vehicle=v).aggregate(Sum('cost'))['cost__sum'] or 0
        total = float(fuel_cost) + float(maint_cost)
        if total > 0:
            cost_data.append({
                'label': v.registration_number,
                'fuel': float(fuel_cost),
                'maintenance': float(maint_cost),
                'total': total
            })
            
    # 2. Fuel Efficiency (km/L)
    efficiency_data = []
    for v in vehicles:
        trips = Trip.objects.filter(vehicle=v, status='Completed', actual_distance__gt=0, fuel_consumed__gt=0)
        total_dist = sum(t.actual_distance for t in trips)
        total_fuel = sum(t.fuel_consumed for t in trips)
        if total_fuel > 0:
            efficiency_data.append({
                'label': v.registration_number,
                'efficiency': float(total_dist / total_fuel)
            })
            
    return JsonResponse({
        'cost_data': cost_data,
        'efficiency_data': efficiency_data
    })

@role_required('Financial Analyst', 'Fleet Manager', 'Admin')
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fleet_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Registration Number', 'Model', 'Status', 'Odometer (km)', 'Fuel Cost ($)', 'Maintenance Cost ($)', 'Total Cost ($)'])
    
    vehicles = Vehicle.objects.all()
    for v in vehicles:
        fuel_cost = FuelLog.objects.filter(vehicle=v).aggregate(Sum('cost'))['cost__sum'] or 0
        maint_cost = MaintenanceLog.objects.filter(vehicle=v).aggregate(Sum('cost'))['cost__sum'] or 0
        total = fuel_cost + maint_cost
        writer.writerow([
            v.registration_number,
            v.name_model,
            v.status,
            v.odometer,
            fuel_cost,
            maint_cost,
            total
        ])
        
    return response
