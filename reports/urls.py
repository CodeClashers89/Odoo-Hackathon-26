from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_view, name='reports'),
    path('api/data/', views.reports_data, name='reports_data'),
    path('export/csv/', views.export_csv, name='export_csv'),
]
