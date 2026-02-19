"""
URL configuration for assessment app
"""
from django.urls import path
from . import views

app_name = 'assessment'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Assessment
    path('assessment/new/', views.new_assessment, name='new_assessment'),
    path('assessment/result/<uuid:applicant_id>/', views.assessment_result, name='assessment_result'),

    # Dashboard and Reports
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/<uuid:applicant_id>/', views.report, name='report'),

    # Applicant Management
    path('applicants/', views.applicant_list, name='applicant_list'),
    path('applicants/<uuid:applicant_id>/', views.applicant_detail, name='applicant_detail'),
    path('applicants/<uuid:applicant_id>/delete/', views.delete_applicant, name='delete_applicant'),

    # API endpoints
    path('api/stats/', views.api_prediction_stats, name='api_prediction_stats'),
]
