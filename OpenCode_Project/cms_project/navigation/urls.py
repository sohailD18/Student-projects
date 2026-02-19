from django.urls import path
from . import views

app_name = 'navigation'

urlpatterns = [
    path('', views.NavigationListView.as_view(), name='navigation_list'),
    path('create/', views.NavigationCreateView.as_view(), name='navigation_create'),
    path('<int:pk>/', views.NavigationDetailView.as_view(), name='navigation_detail'),
    path('<int:pk>/edit/', views.NavigationUpdateView.as_view(), name='navigation_update'),
    path('<int:pk>/delete/', views.NavigationDeleteView.as_view(), name='navigation_delete'),
    path('item/create/', views.NavigationItemCreateView.as_view(), name='navigation_item_create'),
    path('item/<int:pk>/edit/', views.NavigationItemUpdateView.as_view(), name='navigation_item_update'),
    path('item/<int:pk>/delete/', views.NavigationItemDeleteView.as_view(), name='navigation_item_delete'),
    path('footer/', views.FooterLinkListView.as_view(), name='footer_link_list'),
    path('footer/create/', views.FooterLinkCreateView.as_view(), name='footer_link_create'),
    path('footer/<int:pk>/edit/', views.FooterLinkUpdateView.as_view(), name='footer_link_update'),
    path('footer/<int:pk>/delete/', views.FooterLinkDeleteView.as_view(), name='footer_link_delete'),
]
