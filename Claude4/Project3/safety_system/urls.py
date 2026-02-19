"""
Main URL Configuration for AI-Enabled Worker Safety System
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import RedirectView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Legacy redirects (for compatibility)
    path('dashboard/', RedirectView.as_view(url='/monitoring/dashboard/', permanent=False)),
    path('reports/', RedirectView.as_view(url='/monitoring/reports/', permanent=False)),
    path('settings/', RedirectView.as_view(url='/monitoring/settings/', permanent=False)),
    path('video-feed/', RedirectView.as_view(url='/monitoring/video-feed/', permanent=False)),

    # Root redirect to dashboard
    path('', RedirectView.as_view(url='/monitoring/dashboard/', permanent=False), name='root'),

    # Monitoring app URLs
    path('monitoring/', include('monitoring.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
