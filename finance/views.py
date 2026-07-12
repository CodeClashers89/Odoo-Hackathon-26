from django.shortcuts import render, redirect
from accounts.decorators import role_required
from django.contrib import messages
from django.db.models import Sum
from .models import FuelLog, Expense
from .forms import FuelLogForm, ExpenseForm

@role_required('Financial Analyst', 'Fleet Manager', 'Admin')
def finance_list(request):
    # Fuel Logs
    fuel_logs = FuelLog.objects.select_related('vehicle').all()
    
    # Trip-based expenses
    from trips.models import Trip
    from maintenance.models import MaintenanceLog
    
    recent_trips = Trip.objects.select_related('vehicle').order_by('-created_at')[:15]
    
    trip_expenses = []
    total_tolls = 0
    total_other = 0
    total_maint = 0
    
    for trip in recent_trips:
        # Aggregate expenses
        tolls = trip.expenses.filter(expense_type='Toll').aggregate(total=Sum('amount'))['total'] or 0
        other = trip.expenses.exclude(expense_type__in=['Toll', 'Maintenance']).aggregate(total=Sum('amount'))['total'] or 0
        
        # Maint (Linked) - for now, just sum all maintenance for this vehicle
        maint = MaintenanceLog.objects.filter(vehicle=trip.vehicle).aggregate(total=Sum('cost'))['total'] or 0
        
        row_total = tolls + other + maint
        
        trip_expenses.append({
            'trip': trip,
            'vehicle': trip.vehicle,
            'tolls': tolls,
            'other': other,
            'maint': maint,
            'total': row_total,
            'status': trip.status,
        })
        
        total_tolls += tolls
        total_other += other
        
    # We shouldn't double count maintenance if a vehicle is in multiple trips, 
    # but for the footer we'll calculate global totals.
    global_fuel = FuelLog.objects.aggregate(total=Sum('cost'))['total'] or 0
    global_maint = MaintenanceLog.objects.aggregate(total=Sum('cost'))['total'] or 0
    global_tolls = Expense.objects.filter(expense_type='Toll').aggregate(total=Sum('amount'))['total'] or 0
    global_other = Expense.objects.exclude(expense_type__in=['Toll', 'Maintenance']).aggregate(total=Sum('amount'))['total'] or 0
    
    grand_total = global_fuel + global_maint + global_tolls + global_other
    
    # Fetch Maintenance Logs for display
    maintenance_logs = MaintenanceLog.objects.select_related('vehicle').all()
    
    context = {
        'fuel_logs': fuel_logs,
        'trip_expenses': trip_expenses,
        'maintenance_logs': maintenance_logs,
        'grand_total': grand_total,
    }
    return render(request, 'finance/list.html', context)

@role_required('Financial Analyst', 'Fleet Manager', 'Admin')
def fuel_log_add(request):
    if request.method == 'POST':
        form = FuelLogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fuel log added successfully.')
            return redirect('finance_list')
    else:
        form = FuelLogForm()
    return render(request, 'finance/form.html', {'form': form, 'action': 'Add Fuel Log'})

@role_required('Financial Analyst', 'Fleet Manager', 'Admin')
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('finance_list')
    else:
        form = ExpenseForm()
    return render(request, 'finance/form.html', {'form': form, 'action': 'Add Expense'})
