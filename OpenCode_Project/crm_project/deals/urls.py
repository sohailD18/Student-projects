"""
URL configuration for deals app
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.deal_list, name='deal_list'),
    path('kanban/', views.deal_kanban, name='deal_kanban'),
    path('new/', views.DealCreateView.as_view(), name='deal_create'),
    path('update-stage/', views.update_deal_stage, name='update_deal_stage'),
    path('reports/', views.reports, name='deal_reports'),
    path('pipeline/', views.deal_pipeline_setup, name='pipeline_setup'),
    
    path('<int:pk>/', views.DealDetailView.as_view(), name='deal_detail'),
    path('<int:pk>/edit/', views.DealUpdateView.as_view(), name='deal_update'),
    path('<int:pk>/delete/', views.DealDeleteView.as_view(), name='deal_delete'),
]
