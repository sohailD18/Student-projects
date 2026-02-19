"""
URL configuration for Core App
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.search_view, name='search'),
    path('about/', views.about_view, name='about'),
]
