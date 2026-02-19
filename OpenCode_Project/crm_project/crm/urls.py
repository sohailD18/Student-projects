"""
URL configuration for crm_project project.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

class LogoutView(auth_views.LogoutView):
    http_method_names = ['get', 'post']

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('contacts.urls')),
    path('deals/', include('deals.urls')),
    path('activities/', include('activities.urls')),
    path('accounts/profile/', RedirectView.as_view(url='/', permanent=False), name='profile'),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
