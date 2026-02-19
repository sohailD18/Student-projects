"""
URL configuration for multi_vendor_marketplace project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from vendor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/profile/', views.profile_redirect, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('vendor.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
