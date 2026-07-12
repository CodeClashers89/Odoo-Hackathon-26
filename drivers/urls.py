from django.urls import path
from . import views

urlpatterns = [
    path('', views.driver_list, name='drivers_list'),
    path('new/', views.driver_create, name='driver_create'),
    path('send-notifications/', views.send_expiry_notifications, name='driver_send_expiry_notifications'),
    path('<int:driver_id>/edit/', views.driver_edit, name='driver_edit'),
    path('<int:driver_id>/update_status/', views.driver_update_status, name='driver_update_status'),
]
