"""
URL configuration for reports app
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Public pages
    path('', views.home, name='home'),

    # Incident reporting
    path('report/', views.report_incident, name='report_incident'),
    path('incident/<int:incident_id>/', views.incident_detail, name='incident_detail'),

    # Citizen dashboard
    path('dashboard/', views.citizen_dashboard, name='citizen_dashboard'),

    # Claims
    path('claim/<int:incident_id>/', views.file_claim, name='file_claim'),

    # Authority endpoints
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('verify/<int:incident_id>/', views.verify_incident, name='verify_incident'),
    path('claims/', views.manage_claims, name='manage_claims'),
    path('claims/<int:claim_id>/', views.update_claim_status, name='update_claim_status'),

    # API
    path('api/get-location/', views.get_location, name='get_location'),
]
