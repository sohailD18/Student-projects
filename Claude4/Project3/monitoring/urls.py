"""
URL Configuration for Monitoring App
"""

from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # Main pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings_page, name='settings'),

    # Video streaming
    path('video-feed/', views.video_feed, name='video_feed'),

    # API endpoints
    path('api/incidents/', views.incidents_api, name='incidents_api'),
    path('api/statistics/', views.statistics_api, name='statistics_api'),
    path('api/status/', views.system_status, name='system_status'),
    path('api/resolve/<int:incident_id>/', views.resolve_incident, name='resolve_incident'),
    path('api/zone/add/', views.add_restricted_zone, name='add_restricted_zone'),
    path('api/clear-all/', views.clear_all_incidents, name='clear_all_incidents'),
]
