"""
URL configuration for vendor app
"""

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/<slug:store_slug>/', views.vendor_store, name='vendor_store'),
    path('', views.home, name='home'),
    
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    path('vendor/register/', views.vendor_register, name='vendor_register'),
    path('vendor/<slug:store_slug>/', views.vendor_store, name='vendor_store'),
    
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/products/new/', views.vendor_product_create, name='vendor_product_create'),
    path('vendor/products/<int:pk>/edit/', views.vendor_product_update, name='vendor_product_update'),
    path('vendor/orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/earnings/', views.vendor_earnings, name='vendor_earnings'),
    path('vendor/payout/request/', views.vendor_request_payout, name='vendor_request_payout'),
    
    path('admin/commissions/', views.admin_commissions, name='admin_commissions'),
    path('admin/payouts/', views.admin_payouts, name='admin_payouts'),
    path('admin/vendors/', views.admin_vendors, name='admin_vendors'),
    path('admin/vendors/<int:vendor_id>/approve/', views.approve_vendor, name='approve_vendor'),
]
