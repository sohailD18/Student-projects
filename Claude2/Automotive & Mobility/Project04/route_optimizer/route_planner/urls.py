"""
URL configuration for Route Planner app
"""
from django.urls import path
from . import views

app_name = 'route_planner'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('profile/', views.profile_page, name='profile'),
]
