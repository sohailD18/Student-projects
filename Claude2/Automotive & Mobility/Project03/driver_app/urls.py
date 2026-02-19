from django.urls import path
from . import views

app_name = 'driver_app'

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),

    # Dashboard
    path('', views.home, name='home'),

    # Add new trip data
    path('add/', views.add_data, name='add_data'),

    # Analyze data (API endpoint)
    path('analyze/', views.analyze, name='analyze'),

    # Trip details
    path('trip/<int:trip_id>/', views.trip_detail, name='trip_detail'),

    # Driver report
    path('report/<str:driver_name>/', views.driver_report, name='driver_report'),

    # API endpoints
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
]
