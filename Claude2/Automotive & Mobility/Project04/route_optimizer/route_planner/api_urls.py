"""
API URL configuration for Route Planner
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.login_user, name='login_user'),
    path('auth/register/', views.register_user, name='register_user'),
    path('auth/logout/', views.logout_user, name='logout_user'),

    # Route planning endpoints
    path('calculate-routes/', views.calculate_routes, name='calculate_routes'),
    path('analytics/', views.get_analytics, name='analytics'),
    path('history/', views.get_route_history, name='route_history'),
    path('export-report/', views.export_report, name='export_report'),
    path('dashboard-stats/', views.get_dashboard_stats, name='dashboard_stats'),
]
