from django.urls import path
from . import views

urlpatterns = [
    path('', views.driver_list, name='drivers_list'),
    path('new/', views.driver_create, name='driver_create'),
]
