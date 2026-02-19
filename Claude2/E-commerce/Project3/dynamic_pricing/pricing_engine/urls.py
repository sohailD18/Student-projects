"""
URL configuration for pricing_engine app.
"""
from django.urls import path
from . import views

app_name = 'pricing_engine'

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.user_profile, name='user_profile'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/analyze/', views.run_ai_analysis, name='run_ai_analysis'),

    # Simulation
    path('simulation/', views.simulation, name='simulation'),

    # API endpoints
    path('api/products/<int:product_id>/update-price/', views.api_update_price, name='api_update_price'),
    path('api/simulate/', views.api_simulate, name='api_simulate'),
    path('api/products/<int:product_id>/suggestion/', views.api_get_ai_suggestion, name='api_get_ai_suggestion'),
]
