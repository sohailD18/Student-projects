"""
URL configuration for productivity_core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # App URLs
    path('', include('tasks.urls')),

    # Redirect root to dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
]
