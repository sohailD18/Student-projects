"""
URL configuration for tracker app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Main views
    path('', views.home, name='home'),
    path('industry/<int:industry_id>/', views.industry_detail, name='industry_detail'),
    path('report/', views.report, name='report'),

    # API endpoints
    path('api/emission_data/', views.api_emission_data, name='api_emission_data'),
    path('api/predictions/<int:industry_id>/', views.api_predictions, name='api_predictions'),
    path('api/carbon_prices/', views.api_carbon_prices, name='api_carbon_prices'),
    path('api/price_analysis/', views.api_price_analysis, name='api_price_analysis'),
    path('api/industry_comparison/', views.api_industry_comparison, name='api_industry_comparison'),
    path('api/all_predictions/', views.industry_predictions_api, name='all_predictions'),
]
