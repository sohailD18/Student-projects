"""
URL configuration for the transactions app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<str:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('performance/', views.model_performance, name='model_performance'),
    path('analysis/', views.fraud_analysis, name='fraud_analysis'),
    path('analysis/download/', views.download_fraud_report, name='download_fraud_report'),

    # API endpoints
    path('api/dashboard-data/', views.dashboard_api_data, name='dashboard_api_data'),
    path('api/predict/', views.api_predict_transaction, name='api_predict'),
    path('api/stats/', views.api_get_transaction_stats, name='api_stats'),
    path('api/recent-activity/', views.api_recent_activity, name='api_recent_activity'),
]
