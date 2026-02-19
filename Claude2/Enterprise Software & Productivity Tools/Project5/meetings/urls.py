"""
URL configuration for the meetings app.
"""
from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('meetings/', views.meeting_list_view, name='meeting_list'),
    path('meetings/<int:pk>/', views.meeting_detail_view, name='meeting_detail'),
    path('meetings/new/', views.create_meeting_view, name='create_meeting'),
    path('meetings/<int:pk>/delete/', views.delete_meeting_view, name='delete_meeting'),
    path('meetings/<int:pk>/rerun-analysis/', views.rerun_analysis_view, name='rerun_analysis'),
    path('analytics/', views.analytics_view, name='analytics'),
]
