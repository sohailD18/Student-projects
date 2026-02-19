from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.plan_trip_view, name='plan_trip'),
    path('history/', views.trip_history, name='trip_history'),
    path('trip/<int:pk>/', views.trip_detail, name='trip_detail'),
    path('trip/<int:pk>/update/', views.trip_update, name='trip_update'),
    path('trip/<int:pk>/delete/', views.trip_delete, name='trip_delete'),
    path('api/estimate/', views.trip_estimate_api, name='trip_estimate_api'),
]
