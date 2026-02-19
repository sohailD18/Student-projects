"""
URL configuration for AgriSense project.
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('analyze/', views.analyze, name='analyze'),
    path('result/<int:analysis_id>/', views.result, name='result'),
    path('history/', views.history, name='history'),
    path('contact/', views.contact, name='contact'),
]
