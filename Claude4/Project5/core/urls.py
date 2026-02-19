"""
URL configuration for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Trip planning
    path('plan-trip/', views.plan_trip, name='plan_trip'),

    # Location search API
    path('api/search-locations/', views.location_search, name='location_search'),

    # About page
    path('about/', views.about, name='about'),
]
