from django.urls import path
from . import views

urlpatterns = [
    path('', views.finance_list, name='finance_list'),
    path('fuel/new/', views.fuel_log_add, name='fuel_log_add'),
    path('expenses/new/', views.expense_add, name='expense_add'),
]
