from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from . import views
from . import admin_views

urlpatterns = [
    path('', include('jobs.urls')),
    path('accounts/', include('accounts.urls')),
    # Redirect /admin/ to /admin-panel/
    path('admin/', lambda request: redirect('/admin-panel/')),
    # Admin panel routes (must come before the catchall)
    path('admin-panel/', admin_views.admin_home, name='admin_home'),
    path('admin-panel/jobs/', admin_views.admin_jobs_list, name='admin_jobs_list'),
    path('admin-panel/jobs/<int:job_id>/delete/', admin_views.delete_job, name='admin_delete_job'),
    path('admin-panel/applications/', admin_views.admin_applications_list, name='admin_applications_list'),
    path('admin-panel/applications/<int:application_id>/', admin_views.admin_application_detail, name='admin_application_detail'),
    path('admin-panel/applications/<int:application_id>/delete/', admin_views.delete_application, name='admin_delete_application'),
    path('admin-panel/categories/', admin_views.admin_categories_list, name='admin_categories_list'),
    path('admin-panel/saved-jobs/', admin_views.admin_saved_jobs_list, name='admin_saved_jobs_list'),
    path('admin-panel/user-profiles/', admin_views.admin_user_profiles_list, name='admin_user_profiles_list'),
    path('admin-panel/users/', admin_views.admin_users_list, name='admin_users_list'),
    # Django admin URLs at /admin-panel/ for add/edit forms
    path('admin-panel/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
