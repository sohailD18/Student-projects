"""
URL configuration for the finance app.
"""
from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.budget_add, name='budget_add'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # API endpoints
    path('api/suggestions/', views.api_category_suggestions, name='api_suggestions'),
    path('api/patterns/', views.api_spending_patterns, name='api_patterns'),
    path('api/forecast/', views.api_budget_forecast, name='api_forecast'),
    path('api/savings/', views.api_savings_opportunities, name='api_savings'),
    path('api/insights/', views.api_insights, name='api_insights'),
    path('api/summary/', views.get_summary_stats, name='api_summary'),

    # Helper actions
    path('insights/<int:pk>/read/', views.mark_insight_read, name='mark_insight_read'),
]
