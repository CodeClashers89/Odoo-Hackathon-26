from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_list, name='vehicles_list'),
    path('new/', views.vehicle_create, name='vehicle_create'),
]
