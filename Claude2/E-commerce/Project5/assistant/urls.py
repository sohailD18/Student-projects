from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Frontend Pages
    path('', views.home, name='home'),
    path('assistant/', views.assistant_page, name='assistant'),
    path('products/', views.products_page, name='products'),
    # path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard disabled
    path('settings/', views.settings_page, name='settings'),

    # Legacy redirect
    path('index/', views.index, name='index'),

    # API Endpoints
    path('api/search/', views.search_products, name='search_products'),
    path('api/compare/', views.compare_products, name='compare_products'),
    path('api/recommendations/', views.get_recommendations, name='get_recommendations'),
    path('api/chat/', views.chat, name='chat'),
    path('api/chat/history/', views.get_chat_history, name='chat_history'),
    path('api/preferences/', views.update_preferences, name='update_preferences'),

    # Wishlist & Insights APIs
    path('api/wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('api/wishlist/', views.get_wishlist, name='get_wishlist'),
    path('api/insights/', views.get_insights, name='get_insights'),
    path('api/insights/generate/', views.generate_insights, name='generate_insights'),
]
