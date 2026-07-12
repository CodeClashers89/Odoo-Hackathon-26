from django.shortcuts import render
from accounts.decorators import role_required

@role_required('Financial Analyst', 'Fleet Manager', 'Admin')
def finance_list(request):
    return render(request, 'finance/list.html')
