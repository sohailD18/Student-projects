from django.urls import path
from . import views

app_name = 'templates'

urlpatterns = [
    path('', views.TemplateListView.as_view(), name='template_list'),
    path('create/', views.TemplateCreateView.as_view(), name='template_create'),
    path('<int:pk>/', views.TemplateDetailView.as_view(), name='template_detail'),
    path('<int:pk>/edit/', views.TemplateUpdateView.as_view(), name='template_update'),
    path('<int:pk>/delete/', views.TemplateDeleteView.as_view(), name='template_delete'),
    path('themes/', views.ThemeListView.as_view(), name='theme_list'),
    path('themes/create/', views.ThemeCreateView.as_view(), name='theme_create'),
]
