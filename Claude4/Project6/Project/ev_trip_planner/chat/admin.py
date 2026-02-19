from django.contrib import admin
from .models import ChatMessage, ChatConversation


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'started_at', 'message_count']
    search_fields = ['user__username']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'is_user_message', 'created_at']
    list_filter = ['is_user_message', 'created_at']
    search_fields = ['message']
