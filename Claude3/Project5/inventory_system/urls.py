"""
URL configuration for inventory_system app.
"""

from django.urls import path
from . import views

app_name = 'inventory_system'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),

    # API for chart data
    path('api/chart-data/<int:product_id>/', views.api_chart_data, name='api_chart_data'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # Product detail
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Run predictions
    path('run-predictions/', views.run_predictions_view, name='run_predictions'),
]
