"""
URL Configuration for FinRisk AI Core App
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Module 1: Financial Behavior Data Collection
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/create/', views.profile_create, name='profile_create'),
    path('profiles/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profiles/<int:profile_id>/transactions/add/', views.transaction_create, name='transaction_create'),
    path('profiles/<int:profile_id>/transactions/', views.transaction_list, name='transaction_list'),

    # Module 2, 3, 4, 5: Analysis & Risk Profiling
    path('profiles/<int:pk>/analyze/', views.analyze_profile, name='analyze_profile'),

    # Module 6: Visualization Dashboard
    path('profiles/<int:pk>/dashboard/', views.dashboard, name='dashboard'),

    # Module 7: Scenario Calculator
    path('profiles/<int:pk>/scenario/', views.scenario_calculator, name='scenario_calculator'),
    path('api/calculate-scenario/', views.calculate_scenario, name='calculate_scenario'),

    # Module 8: Financial Reports
    path('profiles/<int:pk>/report/', views.financial_report, name='financial_report'),

    # API Endpoints
    path('api/profiles/<int:pk>/stats/', views.api_profile_stats, name='api_profile_stats'),
    path('api/transactions/<int:pk>/delete/', views.delete_transaction, name='delete_transaction'),
]
