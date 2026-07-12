from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.decorators import role_required
from .forms import StaffAccountForm
from drivers.models import Driver
import datetime

@role_required('Admin')
def user_list(request):
    users = User.objects.all().select_related('profile').order_by('username')
    return render(request, 'accounts/list.html', {'users': users})

@role_required('Admin')
def user_create(request):
    if request.method == 'POST':
        form = StaffAccountForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            if role == 'Driver' and not hasattr(user, 'driver_profile'):
                Driver.objects.create(
                    user=user,
                    name=f"{user.first_name} {user.last_name}".strip() or user.username,
                    license_number=f"PENDING-{user.id}",
                    license_category='Light',
                    license_expiry_date=datetime.date.today(),
                    contact_number=user.profile.phone_number or '',
                    status='Available'
                )
            messages.success(request, f'User account for {user.username} created successfully.')
            return redirect('accounts_list')
    else:
        form = StaffAccountForm()
    return render(request, 'accounts/form.html', {'form': form, 'action': 'Create'})

@role_required('Admin')
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = StaffAccountForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            if role == 'Driver' and not hasattr(user, 'driver_profile'):
                Driver.objects.create(
                    user=user,
                    name=f"{user.first_name} {user.last_name}".strip() or user.username,
                    license_number=f"PENDING-{user.id}",
                    license_category='Light',
                    license_expiry_date=datetime.date.today(),
                    contact_number=user.profile.phone_number or '',
                    status='Available'
                )
            messages.success(request, f'User account for {user.username} updated successfully.')
            return redirect('accounts_list')
    else:
        form = StaffAccountForm(instance=user)
    return render(request, 'accounts/form.html', {'form': form, 'action': 'Edit', 'edit_user': user})

@role_required('Admin')
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You cannot delete your own admin account.")
        return redirect('accounts_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User account {username} deleted successfully.')
        return redirect('accounts_list')
    return render(request, 'accounts/delete_confirm.html', {'user_to_delete': user})

