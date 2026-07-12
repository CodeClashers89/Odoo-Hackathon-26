from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='accounts_list'),
    path('new/', views.user_create, name='accounts_create'),
    path('<int:user_id>/edit/', views.user_edit, name='accounts_edit'),
    path('<int:user_id>/delete/', views.user_delete, name='accounts_delete'),
]

