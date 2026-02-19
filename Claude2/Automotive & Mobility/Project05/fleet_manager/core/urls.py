"""
URL configuration for the core app
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Index/Home
    path('', views.index, name='index'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Vehicles
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),

    # Reports
    path('reports/', views.report_view, name='report_view'),
    path('reports/export/', views.export_report, name='export_report'),

    # AJAX/API endpoints
    path('api/alerts/refresh/', views.refresh_alerts, name='refresh_alerts'),
    path('api/vehicles/<int:vehicle_id>/stats/', views.get_vehicle_stats, name='get_vehicle_stats'),
    path('api/alerts/<int:alert_id>/dismiss/', views.dismiss_alert, name='dismiss_alert'),
]
