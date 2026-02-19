"""
OptiFlow - AI-Based Business Process Optimizer
URL Configuration for Core App
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('process/<int:process_id>/dashboard/', views.process_dashboard, name='process_dashboard'),

    # Process Management
    path('processes/', views.process_list, name='process_list'),
    path('process/create/', views.process_create, name='process_create'),
    path('process/<int:process_id>/', views.process_detail, name='process_detail'),
    path('process/<int:process_id>/step/create/', views.step_create, name='step_create'),

    # Data Entry
    path('log/entry/', views.log_entry, name='log_entry'),
    path('log/list/', views.log_list, name='log_list'),
    path('log/<int:log_id>/', views.log_detail, name='log_detail'),

    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('process/<int:process_id>/analyze/', views.process_analysis, name='process_analysis'),

    # Recommendations
    path('recommendations/', views.recommendation_list, name='recommendation_list'),
    path('recommendation/<int:rec_id>/', views.recommendation_detail, name='recommendation_detail'),
    path('recommendation/<int:rec_id>/update/', views.recommendation_update_status, name='recommendation_update'),

    # Reporting
    path('reports/optimization/', views.optimization_report, name='optimization_report'),

    # API Endpoints
    path('api/process/<int:process_id>/metrics/', views.api_process_metrics, name='api_process_metrics'),
    path('api/process/<int:process_id>/analyze/', views.api_analyze_process, name='api_analyze_process'),
]
