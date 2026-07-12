"""
URL configuration for transitops project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth URLs (login, logout)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Redirect root to dashboard
    path('', RedirectView.as_view(pattern_name='dashboard'), name='home'),
    
    # App URLs (to be created)
    path('dashboard/', include('dashboard.urls')),
    path('accounts-custom/', include('accounts.urls')),
    path('vehicles/', include('vehicles.urls')),
    path('drivers/', include('drivers.urls')),
    path('trips/', include('trips.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('finance/', include('finance.urls')),
    path('reports/', include('reports.urls')),
]
