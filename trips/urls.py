from django.urls import path
from . import views

urlpatterns = [
    path('', views.trip_list, name='trips_list'),
    path('new/', views.trip_create, name='trip_create'),
    path('<int:trip_id>/dispatch/', views.trip_dispatch, name='trip_dispatch'),
    path('<int:trip_id>/complete/', views.trip_complete, name='trip_complete'),
    path('<int:trip_id>/cancel/', views.trip_cancel, name='trip_cancel'),
]
