from django.db import models
from django.contrib.auth.models import User


class ChatConversation(models.Model):
    """Chat conversation session"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_conversations')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    @property
    def message_count(self):
        return self.messages.count()

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Chat with {self.user.username} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """Individual chat message"""
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    is_user_message = models.BooleanField(default=True)  # True = user, False = AI
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sender = "User" if self.is_user_message else "AI"
        return f"{sender}: {self.message[:50]}..."
