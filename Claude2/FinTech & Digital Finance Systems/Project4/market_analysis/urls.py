"""
URL configuration for market_analysis app
"""

from django.urls import path
from . import views

app_name = 'market_analysis'

urlpatterns = [
    # Template Views
    path('', views.dashboard, name='dashboard'),

    # API: Stock Management
    path('api/stocks/', views.api_stocks_list, name='api_stocks_list'),
    path('api/stocks/<int:stock_id>/', views.api_stock_detail, name='api_stock_detail'),

    # API: Data Ingestion
    path('api/fetch-data/', views.api_fetch_stock_data, name='api_fetch_stock_data'),

    # API: Prediction Engine
    path('api/train-predict/', views.api_train_and_predict, name='api_train_and_predict'),
    path('api/predictions/<int:stock_id>/', views.api_get_predictions, name='api_get_predictions'),

    # API: Volatility and Risk Analysis
    path('api/analyze-volatility/', views.api_analyze_volatility, name='api_analyze_volatility'),

    # API: Market Reports
    path('api/generate-report/', views.api_generate_report, name='api_generate_report'),
    path('api/reports/<int:stock_id>/', views.api_get_reports, name='api_get_reports'),

    # API: Dashboard Data
    path('api/dashboard/<int:stock_id>/', views.api_dashboard_data, name='api_dashboard_data'),
]
