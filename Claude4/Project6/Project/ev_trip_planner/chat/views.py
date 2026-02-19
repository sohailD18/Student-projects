from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import ChatConversation, ChatMessage
from .ai_responses import get_ai_response


@login_required
def chat_interface(request):
    """Main chat interface"""
    # Get or create active conversation
    active_conversation = request.user.chat_conversations.filter(
        ended_at__isnull=True
    ).first()

    if not active_conversation:
        # Create new conversation
        active_conversation = ChatConversation.objects.create(user=request.user)

    # Get recent messages
    messages = active_conversation.messages.all()[:50]

    context = {
        'conversation': active_conversation,
        'messages': messages,
    }
    return render(request, 'chat/chat_interface.html', context)


@login_required
def chat_history(request):
    """View chat history"""
    conversations = request.user.chat_conversations.all()

    context = {
        'conversations': conversations,
    }
    return render(request, 'chat/chat_history.html', context)


@login_required
def conversation_detail(request, pk):
    """View specific conversation"""
    conversation = get_object_or_404(ChatConversation, pk=pk, user=request.user)
    messages = conversation.messages.all()

    context = {
        'conversation': conversation,
        'messages': messages,
    }
    return render(request, 'chat/conversation_detail.html', context)


@login_required
def start_new_chat(request):
    """Start a new conversation"""
    # End any active conversations
    request.user.chat_conversations.filter(ended_at__isnull=True).update(
        ended_at=timezone.now()
    )

    # Create new conversation
    new_conversation = ChatConversation.objects.create(user=request.user)

    # Add welcome message
    welcome_message = """Hello! I'm your EV Charging Assistant. I can help you with:

• 📍 Finding charging stations
• 🗺️ Planning your trips
• 🔋 Battery maintenance tips
• ⚡ Charging information
• 💰 Cost comparisons
• 🚗 EV recommendations

How can I help you today?"""

    ChatMessage.objects.create(
        conversation=new_conversation,
        is_user_message=False,
        message=welcome_message
    )

    return redirect('chat:chat_interface')


@login_required
def send_message(request):
    """Handle AJAX message sending"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'success': False, 'error': 'Empty message'})

        # Get active conversation
        conversation = request.user.chat_conversations.filter(
            ended_at__isnull=True
        ).first()

        if not conversation:
            conversation = ChatConversation.objects.create(user=request.user)

        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            is_user_message=True,
            message=user_message
        )

        # Get AI response
        ai_response_text, category = get_ai_response(user_message)

        # Save AI response
        ChatMessage.objects.create(
            conversation=conversation,
            is_user_message=False,
            message=ai_response_text
        )

        return JsonResponse({
            'success': True,
            'user_message': user_message,
            'ai_response': ai_response_text,
            'category': category,
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def end_conversation(request):
    """End current conversation"""
    if request.method == 'POST':
        active_conversation = request.user.chat_conversations.filter(
            ended_at__isnull=True
        ).first()

        if active_conversation:
            active_conversation.ended_at = timezone.now()
            active_conversation.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# Floating chat widget endpoint (for use on other pages)
@login_required
def chat_widget_api(request):
    """API for floating chat widget"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'success': False, 'error': 'Empty message'})

        # Get or create active conversation
        conversation = request.user.chat_conversations.filter(
            ended_at__isnull=True
        ).first()

        if not conversation:
            conversation = ChatConversation.objects.create(user=request.user)

        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            is_user_message=True,
            message=user_message
        )

        # Get AI response
        ai_response_text, category = get_ai_response(user_message)

        # Save AI response
        ChatMessage.objects.create(
            conversation=conversation,
            is_user_message=False,
            message=ai_response_text
        )

        return JsonResponse({
            'success': True,
            'response': ai_response_text,
            'category': category,
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'})
