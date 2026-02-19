from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Transactions
    path('', views.dashboard, name='dashboard'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),

    # Alerts
    path('alerts/', views.alerts, name='alerts'),
    path('alerts/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    path('alerts/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    path('alerts/<int:alert_id>/create-case/', views.create_case_from_alert, name='create_case_from_alert'),

    # User Profiles & Spending Patterns
    path('profiles/', views.user_profiles, name='user_profiles'),
    path('profiles/<str:user>/', views.user_profile_detail, name='user_profile_detail'),
    path('profiles/<str:user>/update/', views.update_user_profile, name='update_user_profile'),

    # Fraud Cases
    path('cases/', views.fraud_cases, name='fraud_cases'),
    path('cases/create/', views.create_case, name='create_case'),
    path('cases/<str:case_id>/', views.case_detail, name='case_detail'),
    path('cases/<str:case_id>/update/', views.update_case_status, name='update_case_status'),
    path('cases/<str:case_id>/note/', views.add_case_note, name='add_case_note'),

    # Compliance & Reporting
    path('reports/', views.compliance_reports, name='compliance_reports'),
    path('reports/generate/', views.generate_fraud_summary, name='generate_fraud_summary'),
    path('cases/<str:case_id>/sar/', views.generate_sar, name='generate_sar'),
    path('audit-log/', views.audit_log, name='audit_log'),

    # Rules Management
    path('rules/', views.fraud_rules, name='fraud_rules'),
    path('rules/create/', views.create_rule, name='create_rule'),
    path('rules/<int:rule_id>/toggle/', views.toggle_rule, name='toggle_rule'),

    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
]
