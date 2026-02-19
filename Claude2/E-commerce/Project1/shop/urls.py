"""
URL configuration for the shop app.
"""

from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Home & Main Pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Authentication
    path('login/', views.custom_login, name='login'),
    path('register/', views.custom_register, name='register'),
    path('logout/', views.custom_logout, name='logout'),

    # Product Pages
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # Category Pages
    path('category/<int:category_id>/', views.category_products, name='category'),

    # Analytics & Reports
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('export/csv/', views.export_interactions_csv, name='export_csv'),
    path('export/csv/filtered/', views.export_interactions_csv_filtered, name='export_csv_filtered'),

    # Interaction Tracking (AJAX)
    path('track/', views.track_interaction, name='track_interaction'),
]
