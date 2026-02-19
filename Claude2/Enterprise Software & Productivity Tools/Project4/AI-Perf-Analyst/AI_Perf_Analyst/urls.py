"""
URL configuration for AI_Perf_Analyst project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('performance.urls')),
]
