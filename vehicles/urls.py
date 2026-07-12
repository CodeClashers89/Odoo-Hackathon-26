from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_list, name='vehicles_list'),
    path('new/', views.vehicle_create, name='vehicle_create'),
    path('<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('<int:vehicle_id>/edit/', views.vehicle_edit, name='vehicle_edit'),
]
