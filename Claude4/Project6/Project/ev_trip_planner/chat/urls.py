from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'chat'

urlpatterns = [
    path('', lambda request: redirect('core:home'), name='chat_interface'),
    path('history/', views.chat_history, name='chat_history'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('new/', views.start_new_chat, name='start_new_chat'),
    path('send/', views.send_message, name='send_message'),
    path('end/', views.end_conversation, name='end_conversation'),
    path('api/widget/', views.chat_widget_api, name='chat_widget_api'),
]
