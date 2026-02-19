"""
URL configuration for Users App
"""
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-exams/', views.my_exams_view, name='my_exams'),
]
