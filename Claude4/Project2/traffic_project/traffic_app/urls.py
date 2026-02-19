"""
URL Configuration for Traffic App

This module defines the URL patterns for the traffic prediction application.
It maps URLs to view functions and creates named URL patterns for reverse routing.
"""

from django.urls import path
from . import views

# Namespace for traffic_app URLs
app_name = 'traffic_app'

urlpatterns = [
    # Home / Dashboard
    path('', views.home, name='home'),

    # Prediction Page & API
    path('predict/', views.predict, name='predict'),
    path('api/predict/', views.predict_api, name='predict_api'),

    # Analysis Page & API
    path('analysis/', views.analysis, name='analysis'),
    path('api/analysis/', views.analysis_api, name='analysis_api'),

    # Utility APIs
    path('api/locations/', views.get_locations, name='get_locations'),
]
