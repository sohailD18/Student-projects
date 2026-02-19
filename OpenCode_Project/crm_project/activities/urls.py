"""
URL configuration for activities app
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
    path('calendar/', views.activity_calendar, name='activity_calendar'),
    path('tasks/', views.task_list, name='task_list'),
    path('feed/', views.activity_feed, name='activity_feed'),
    path('new/', views.ActivityCreateView.as_view(), name='activity_create'),
    path('quick/', views.quick_activity, name='quick_activity'),
    path('<int:pk>/edit/', views.ActivityUpdateView.as_view(), name='activity_update'),
    path('<int:pk>/delete/', views.ActivityDeleteView.as_view(), name='activity_delete'),
    path('<int:activity_id>/complete/', views.complete_activity, name='complete_activity'),
]
