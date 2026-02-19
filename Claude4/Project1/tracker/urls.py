from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('add/', views.add_transaction_view, name='add_transaction'),
    path('delete/<int:transaction_id>/', views.delete_transaction_view, name='delete_transaction'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]
