"""
URL Configuration for Inventory App

Defines URL patterns for the inventory management system.
"""

from django.urls import path
from . import views
from . import auth_views

app_name = 'inventory'

urlpatterns = [
    # Authentication Views
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),

    # Main Views
    path('', views.dashboard, name='dashboard'),

    # API Endpoints - Forecasting
    path('api/forecast/all/', views.api_forecast_all, name='api_forecast_all'),
    path('api/forecast/<int:product_id>/', views.api_forecast_product, name='api_forecast_product'),
    path('api/forecast/<int:product_id>/confidence/', views.api_forecast_with_confidence, name='api_forecast_with_confidence'),

    # API Endpoints - Charts and Visualization
    path('api/chart/<int:product_id>/', views.api_product_chart_data, name='api_product_chart_data'),
    path('api/sales/<int:product_id>/', views.api_sales_data, name='api_sales_data'),

    # API Endpoints - Dashboard
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/inventory/summary/', views.api_inventory_summary, name='api_inventory_summary'),

    # API Endpoints - Products
    path('api/products/', views.api_products_list, name='api_products_list'),

    # API Endpoints - Enhanced Analytics
    path('api/trend/<int:product_id>/', views.api_trend_analysis, name='api_trend_analysis'),
    path('api/trends/all/', views.api_all_trends, name='api_all_trends'),
    path('api/accuracy/<int:product_id>/', views.api_model_accuracy, name='api_model_accuracy'),
    path('api/report/<int:product_id>/comprehensive/', views.api_comprehensive_report, name='api_comprehensive_report'),

    # API Endpoints - Reports
    path('api/reports/replenishment/', views.api_replenishment_report, name='api_replenishment_report'),

    # Health Check
    path('health/', views.health_check, name='health_check'),
]
