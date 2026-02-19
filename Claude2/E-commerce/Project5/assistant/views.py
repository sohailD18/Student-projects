from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import json
import uuid
import re
from .models import (
    Product, UserPreference, ChatSession, ChatMessage, InteractionHistory,
    UserProfile, Wishlist, PurchaseHistory, RecommendationHistory, UserInsight
)


# ============================================
# AUTHENTICATION VIEWS
# ============================================

def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not all([username, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'assistant/register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'assistant/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'assistant/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'assistant/register.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create user profile
        UserProfile.objects.create(user=user)

        # Create user preferences
        UserPreference.objects.create(
            user_id=username,
            preferred_categories=[],
            budget_range={'min': 0, 'max': 5000},
            style_tags=[]
        )

        messages.success(request, 'Account created successfully! Please login.')
        return redirect('assistant:login')

    return render(request, 'assistant/register.html')


def login_view(request):
    """User login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect to next page or home
            next_page = request.GET.get('next', 'assistant:home')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'assistant/login.html')


@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('assistant:home')


# ============================================
# FRONTEND VIEWS
# ============================================

def home(request):
    """Enhanced home page with hero section and featured products."""
    # Get featured products (top rated)
    featured_products = Product.objects.order_by('-rating')[:6]

    # Get categories for display
    categories = Product.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:6]

    context = {
        'featured_products': featured_products,
        'categories': list(categories),
        'user': request.user if request.user.is_authenticated else None,
    }
    return render(request, 'assistant/home.html', context)


def products_page(request):
    """Products page with grid and filtering."""
    products = Product.objects.all().order_by('-rating')[:20]

    context = {
        'products': products,
        'user': request.user if request.user.is_authenticated else None,
    }
    return render(request, 'assistant/products.html', context)


@login_required
def dashboard(request):
    """User dashboard with insights, history, and recommendations."""
    user = request.user

    # Get user profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get purchase history
    purchases = PurchaseHistory.objects.filter(user=user).select_related('product')[:10]

    # Get wishlist
    wishlist_items = Wishlist.objects.filter(user=user).select_related('product')[:10]

    # Get unread insights
    insights = UserInsight.objects.filter(user=user, is_read=False)[:5]

    # Calculate statistics
    total_spent = PurchaseHistory.objects.filter(user=user).aggregate(
        total=Sum('price_at_purchase')
    )['total'] or 0

    total_purchases = PurchaseHistory.objects.filter(user=user).count()

    # Get recent interactions
    recent_interactions = InteractionHistory.objects.filter(
        user_id=user.username
    ).order_by('-timestamp')[:10]

    # Get personalized recommendations
    try:
        preferences = UserPreference.objects.get(user_id=user.username)
        recommended_products = Product.objects.filter(
            category__in=preferences.preferred_categories
        ).order_by('-rating')[:6] if preferences.preferred_categories else []
    except UserPreference.DoesNotExist:
        recommended_products = Product.objects.order_by('-rating')[:6]

    context = {
        'profile': profile,
        'purchases': purchases,
        'wishlist_items': wishlist_items,
        'insights': insights,
        'total_spent': total_spent,
        'total_purchases': total_purchases,
        'recommended_products': recommended_products,
        'recent_interactions': recent_interactions,
    }
    return render(request, 'assistant/dashboard.html', context)


@login_required
def settings_page(request):
    """User settings and profile page."""
    user = request.user

    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get user preferences
    try:
        preferences = UserPreference.objects.get(user_id=user.username)
    except UserPreference.DoesNotExist:
        preferences = UserPreference.objects.create(
            user_id=user.username,
            preferred_categories=[],
            budget_range={'min': 0, 'max': 5000},
            style_tags=[]
        )

    if request.method == 'POST':
        # Update profile
        profile.phone = request.POST.get('phone')
        profile.default_budget_min = float(request.POST.get('budget_min', 0))
        profile.default_budget_max = float(request.POST.get('budget_max', 5000))
        profile.save()

        # Update preferences
        categories = request.POST.getlist('categories')
        preferences.preferred_categories = categories
        preferences.budget_range = {
            'min': profile.default_budget_min,
            'max': profile.default_budget_max
        }
        preferences.save()

        messages.success(request, 'Settings updated successfully!')
        return redirect('assistant:settings')

    context = {
        'profile': profile,
        'preferences': preferences,
        'all_categories': Product.objects.values_list('category', flat=True).distinct(),
    }
    return render(request, 'assistant/settings.html', context)


def assistant_page(request):
    """AI Assistant page with chat, products, and comparison."""
    context = {
        'user': request.user if request.user.is_authenticated else None,
    }
    return render(request, 'assistant/assistant.html', context)


def index(request):
    """Legacy index - redirects to home."""
    return redirect('assistant:home')


# ============================================
# SEARCH & FILTER
# ============================================

@require_http_methods(["GET"])
def search_products(request):
    """
    Search and filter products based on query parameters.
    Query params:
    - q: search query text
    - category: filter by category
    - min_price: minimum price
    - max_price: maximum price
    - min_rating: minimum rating
    """
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')

    products = Product.objects.all()

    # Text search
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    # Category filter
    if category:
        products = products.filter(category__iexact=category)

    # Price range filter
    if min_price:
        products = products.filter(price__gte=float(min_price))
    if max_price:
        products = products.filter(price__lte=float(max_price))

    # Rating filter
    if min_rating:
        products = products.filter(rating__gte=float(min_rating))

    # Serialize products
    products_data = [
        {
            'id': str(product.id),
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'category': product.category,
            'image_url': product.image_url,
            'specs': product.specs,
            'rating': product.rating,
            'badges': _get_product_badges(product)
        }
        for product in products[:20]  # Limit to 20 results
    ]

    return JsonResponse({
        'success': True,
        'products': products_data,
        'count': len(products_data)
    })


def _get_product_badges(product):
    """Generate decision support badges for a product."""
    badges = []

    if product.rating >= 4.8:
        badges.append('Top Rated')

    # Get average price for category
    avg_price = Product.objects.filter(
        category=product.category
    ).aggregate(Avg('price'))['price__avg'] or 0

    if product.price < float(avg_price) * 0.8 and product.rating >= 4.5:
        badges.append('Best Value')

    if product.price >= 2000:
        badges.append('Premium')

    return badges


# ============================================
# COMPARISON ENGINE
# ============================================

@require_http_methods(["POST"])
@csrf_exempt
def compare_products(request):
    """
    Compare multiple products side-by-side.
    Expects: {'product_ids': ['id1', 'id2', ...]}
    """
    try:
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])

        if len(product_ids) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Please select at least 2 products to compare'
            })

        if len(product_ids) > 4:
            return JsonResponse({
                'success': False,
                'error': 'Cannot compare more than 4 products at once'
            })

        products = Product.objects.filter(id__in=product_ids)

        # Build comparison data
        comparison = {
            'products': [],
            'summary': _generate_comparison_summary(products)
        }

        for product in products:
            comparison['products'].append({
                'id': str(product.id),
                'name': product.name,
                'price': float(product.price),
                'category': product.category,
                'image_url': product.image_url,
                'specs': product.specs,
                'rating': product.rating,
                'badges': _get_product_badges(product)
            })

        return JsonResponse({'success': True, 'comparison': comparison})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def _generate_comparison_summary(products):
    """Generate an AI-like comparison summary."""
    if not products:
        return ""

    prices = [p.price for p in products]
    ratings = [p.rating for p in products]

    cheapest = products[prices.index(min(prices))]
    highest_rated = products[ratings.index(max(ratings))]

    summary = f"💡 **Comparison Summary**\n\n"
    summary += f"🏆 **Best Rated:** {highest_rated.name} ({highest_rated.rating}⭐)\n"
    summary += f"💰 **Most Affordable:** {cheapest.name} (${cheapest.price})\n\n"

    if len(products) == 2:
        summary += "**Verdict:** "
        if cheapest == highest_rated:
            summary += f"The {cheapest.name} offers the best value with top ratings at a great price."
        else:
            summary += f"If budget is a priority, go with {cheapest.name}. "
            summary += f"For the best experience, {highest_rated.name} is worth the extra investment."

    return summary


# ============================================
# RECOMMENDATION SYSTEM
# ============================================

@require_http_methods(["GET"])
def get_recommendations(request):
    """
    Get personalized recommendations based on user preferences.
    Query params:
    - user_id: user identifier
    - category: optional category filter
    - limit: number of recommendations (default: 6)
    """
    user_id = request.GET.get('user_id', 'anonymous')
    category = request.GET.get('category', '')
    limit = int(request.GET.get('limit', 6))

    try:
        # Get or create user preferences
        preferences, created = UserPreference.objects.get_or_create(
            user_id=user_id,
            defaults={
                'preferred_categories': [],
                'budget_range': {'min': 0, 'max': 5000},
                'style_tags': []
            }
        )

        # Start with all products
        products = Product.objects.all()

        # Filter by preferred categories
        if preferences.preferred_categories and not category:
            products = products.filter(
                category__in=preferences.preferred_categories
            )

        # Filter by specific category if provided
        if category:
            products = products.filter(category=category)

        # Filter by budget range
        budget_min = preferences.budget_range.get('min', 0)
        budget_max = preferences.budget_range.get('max', 10000)
        products = products.filter(
            price__gte=budget_min,
            price__lte=budget_max
        )

        # Sort by rating and limit
        products = products.order_by('-rating')[:limit]

        recommendations = [
            {
                'id': str(product.id),
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'category': product.category,
                'image_url': product.image_url,
                'specs': product.specs,
                'rating': product.rating,
                'badges': _get_product_badges(product),
                'reason': _get_recommendation_reason(product, preferences)
            }
            for product in products
        ]

        return JsonResponse({
            'success': True,
            'recommendations': recommendations,
            'preferences': {
                'categories': preferences.preferred_categories,
                'budget_range': preferences.budget_range
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def _get_recommendation_reason(product, preferences):
    """Generate a reason for the recommendation."""
    reasons = []

    if product.rating >= 4.7:
        reasons.append("highly rated by customers")

    if preferences.budget_range.get('max', 10000):
        avg_price = Product.objects.filter(
            category=product.category
        ).aggregate(Avg('price'))['price__avg'] or 0
        if product.price < float(avg_price):
            reasons.append("great value for money")

    if product.category in preferences.preferred_categories:
        reasons.append(f"matches your interest in {product.category}s")

    return "Recommended because it's " + " and ".join(reasons) if reasons else "Great choice for your needs"


# ============================================
# CONVERSATIONAL AI INTERFACE (MOCK AI)
# ============================================

@require_http_methods(["POST"])
@csrf_exempt
def chat(request):
    """
    Main chat endpoint with Mock AI Service.
    Expects: {'message': 'user message', 'session_id': 'optional'}
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')

        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            })

        # Get or create chat session
        if session_id:
            session = ChatSession.objects.filter(session_id=session_id).first()
        else:
            session = ChatSession.objects.create()
            session_id = str(session.session_id)

        # Save user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )

        # Process message with Mock AI
        ai_response = _mock_ai_process(user_message, session)

        # Save AI response
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=ai_response['text']
        )

        # Track interaction
        InteractionHistory.objects.create(
            user_id=f"session_{session_id}",
            query_text=user_message,
            interaction_type='view',
            session=session
        )

        return JsonResponse({
            'success': True,
            'response': ai_response,
            'session_id': session_id
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def _mock_ai_process(message, session):
    """
    Mock AI Service - Simulates intelligent responses.
    Structure this to easily swap in real OpenAI/Anthropic API later.
    """
    message_lower = message.lower()

    # Intent detection with regex patterns
    patterns = {
        'show_products': r'(show|display|list|find|search|get|what).*(laptops?|phones?|headphones?|products?)',
        'under_price': r'(under|below|less than|cheaper than|budget).*\$(\d+)',
        'compare': r'(compare|vs|versus|difference|better|which is)',
        'recommend': r'(recommend|suggest|best|top|good).*\$(\d+)?',
        'greeting': r'^(hi|hello|hey|help)',
        'specs': r'(specs?|specifications?|details?|features?)',
    }

    # Greeting
    if re.search(patterns['greeting'], message_lower):
        return {
            'text': "👋 Hello! I'm your Smart Shopping Assistant. I can help you:\n\n"
                   "• Find products within your budget\n"
                   "• Compare different products\n"
                   "• Get personalized recommendations\n"
                   "• Answer product questions\n\n"
                   "Try asking: 'Show me laptops under $1000' or 'Compare iPhone vs Samsung'",
            'type': 'greeting',
            'products': []
        }

    # Product search with price
    price_match = re.search(patterns['under_price'], message_lower)
    category_match = re.search(r'(laptops?|phones?|headphones?)', message_lower)

    if price_match and category_match:
        max_price = int(price_match.group(2))
        category = category_match.group(1).rstrip('s')

        products = Product.objects.filter(
            category__iexact=category,
            price__lte=max_price
        ).order_by('-rating')[:5]

        if products.exists():
            product_list = "\n".join([
                f"• {p.name} - ${p.price} ⭐{p.rating}"
                for p in products
            ])

            return {
                'text': f"🔍 Found {products.count()} {category}s under ${max_price}:\n\n{product_list}\n\n"
                       f"Would you like more details or a comparison?",
                'type': 'product_search',
                'products': [_serialize_product(p) for p in products]
            }
        else:
            return {
                'text': f"😔 Sorry, I couldn't find any {category}s under ${max_price}. "
                       f"Would you like to see options in a higher price range?",
                'type': 'no_results',
                'products': []
            }

    # General product search
    if re.search(patterns['show_products'], message_lower):
        category_match = re.search(r'(laptops?|phones?|headphones?)', message_lower)

        if category_match:
            category = category_match.group(1).rstrip('s')
            products = Product.objects.filter(
                category__iexact=category
            ).order_by('-rating')[:6]

            product_list = "\n".join([
                f"• {p.name} - ${p.price} ⭐{p.rating}"
                for p in products
            ])

            return {
                'text': f"📱 Here are our top {category}s:\n\n{product_list}",
                'type': 'product_list',
                'products': [_serialize_product(p) for p in products]
            }

    # Comparison request
    if re.search(patterns['compare'], message_lower):
        # Extract product names from message (simple version)
        words = message_lower.split()
        mentioned_products = Product.objects.filter(
            name__icontains=words[0] if words else ''
        )[:2]

        if mentioned_products.count() >= 2:
            comparison = _generate_comparison_summary(mentioned_products)
            return {
                'text': comparison,
                'type': 'comparison',
                'products': [_serialize_product(p) for p in mentioned_products]
            }

        return {
            'text': "🤔 To compare products, please click the 'Add to Compare' button "
                   "on product cards, or tell me which specific products you'd like to compare.",
            'type': 'info',
            'products': []
        }

    # Recommendation request
    if re.search(patterns['recommend'], message_lower):
        budget_match = re.search(r'\$(\d+)', message)

        if budget_match:
            max_budget = int(budget_match.group(1))
            products = Product.objects.filter(
                price__lte=max_budget
            ).order_by('-rating')[:3]

            if products.exists():
                return {
                    'text': f"⭐ Top recommendations under ${max_budget}:\n\n" +
                           "\n".join([
                               f"• {p.name} - ${p.price} ⭐{p.rating}\n  {_get_recommendation_reason(p, None)}"
                               for p in products
                           ]),
                    'type': 'recommendation',
                    'products': [_serialize_product(p) for p in products]
                }

        # General recommendations
        products = Product.objects.all().order_by('-rating')[:3]

        return {
            'text': f"⭐ Here are our highest-rated products:\n\n" +
                   "\n".join([
                       f"• {p.name} - ${p.price} ⭐{p.rating}"
                       for p in products
                   ]),
            'type': 'recommendation',
            'products': [_serialize_product(p) for p in products]
        }

    # Specs inquiry
    if re.search(patterns['specs'], message_lower):
        # Try to find mentioned product
        words = message_lower.split()
        for word in words:
            if len(word) > 3:
                product = Product.objects.filter(name__icontains=word).first()
                if product:
                    specs_text = "\n".join([
                        f"• **{k.replace('_', ' ').title()}:** {v}"
                        for k, v in product.specs.items()
                    ])

                    return {
                        'text': f"📋 **{product.name}** Specifications:\n\n{specs_text}",
                        'type': 'specs',
                        'products': [_serialize_product(product)]
                    }

    # Default fallback response
    return {
        'text': "I'm here to help you find the perfect product! Here are some things you can ask:\n\n"
               "• 'Show me laptops under $1000'\n"
               "• 'What are the best headphones?'\n"
               "• 'Compare iPhone vs Samsung'\n"
               "• 'Recommend a phone under $500'\n"
               "• 'What are the specs of MacBook Pro?'",
        'type': 'help',
        'products': []
    }


def _serialize_product(product):
    """Serialize product for JSON response."""
    return {
        'id': str(product.id),
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'category': product.category,
        'image_url': product.image_url,
        'specs': product.specs,
        'rating': product.rating,
        'badges': _get_product_badges(product)
    }


# ============================================
# SESSION MANAGEMENT
# ============================================

@require_http_methods(["GET"])
def get_chat_history(request):
    """Get chat history for a session."""
    session_id = request.GET.get('session_id')

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Session ID required'})

    session = ChatSession.objects.filter(session_id=session_id).first()

    if not session:
        return JsonResponse({'success': False, 'error': 'Session not found'})

    messages = ChatMessage.objects.filter(session=session).order_by('timestamp')

    history = [
        {
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        }
        for msg in messages
    ]

    return JsonResponse({'success': True, 'history': history})


@require_http_methods(["POST"])
@csrf_exempt
def update_preferences(request):
    """Update user preferences."""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id', 'anonymous')

        preferences, created = UserPreference.objects.get_or_create(
            user_id=user_id
        )

        if 'categories' in data:
            preferences.preferred_categories = data['categories']

        if 'budget_range' in data:
            preferences.budget_range = data['budget_range']

        if 'style_tags' in data:
            preferences.style_tags = data['style_tags']

        preferences.save()

        return JsonResponse({
            'success': True,
            'preferences': {
                'categories': preferences.preferred_categories,
                'budget_range': preferences.budget_range,
                'style_tags': preferences.style_tags
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# WISHLIST & PURCHASE APIS
# ============================================

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def add_to_wishlist(request):
    """Add product to wishlist."""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')

        product = get_object_or_404(Product, id=product_id)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            wishlist_item.delete()
            return JsonResponse({'success': True, 'action': 'removed'})

        return JsonResponse({'success': True, 'action': 'added'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
@login_required
def get_wishlist(request):
    """Get user's wishlist."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')

    items = [
        {
            'id': str(item.product.id),
            'name': item.product.name,
            'price': float(item.product.price),
            'image_url': item.product.image_url,
            'category': item.product.category,
            'rating': item.product.rating,
            'added_at': item.added_at.isoformat(),
        }
        for item in wishlist_items
    ]

    return JsonResponse({'success': True, 'items': items})


# ============================================
# INSIGHTS & ANALYTICS
# ============================================

@require_http_methods(["GET"])
@login_required
def get_insights(request):
    """Get user shopping insights."""
    user = request.user

    insights = []

    # Purchase history analysis
    purchases = PurchaseHistory.objects.filter(user=user)
    if purchases.exists():
        # Category preference
        category_data = {}
        for purchase in purchases:
            if purchase.product:
                cat = purchase.product.category
                category_data[cat] = category_data.get(cat, 0) + 1

        if category_data:
            top_category = max(category_data, key=category_data.get)
            insights.append({
                'type': 'category_preference',
                'title': f'You love {top_category}s!',
                'description': f'You\'ve purchased {category_data[top_category]} {top_category} products.',
                'icon': '🎯'
            })

        # Average spending
        total_spent = purchases.aggregate(total=Sum('price_at_purchase'))['total'] or 0
        if total_spent > 0:
            insights.append({
                'type': 'spending',
                'title': 'Total Spending',
                'description': f'You\'ve spent ${total_spent:.2f} on {purchases.count()} purchases.',
                'icon': '💰'
            })

    # Recent interactions
    recent_interactions = InteractionHistory.objects.filter(
        user_id=user.username
    ).order_by('-timestamp')[:5]

    return JsonResponse({
        'success': True,
        'insights': insights,
        'recent_interactions': [
            {
                'query': interaction.query_text,
                'type': interaction.interaction_type,
                'timestamp': interaction.timestamp.isoformat()
            }
            for interaction in recent_interactions
        ]
    })


# ============================================
# GENERATE INSIGHTS
# ============================================

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def generate_insights(request):
    """Generate AI-powered insights for user."""
    try:
        user = request.user

        # Clear old insights
        UserInsight.objects.filter(user=user, is_read=False).update(is_read=True)

        # Generate new insights
        purchases = PurchaseHistory.objects.filter(user=user)
        interactions = InteractionHistory.objects.filter(user_id=user.username)

        # Budget trend insight
        if purchases.exists():
            avg_spending = purchases.aggregate(
                avg=Sum('price_at_purchase') / Count('id')
            )['avg'] or 0

            UserInsight.objects.create(
                user=user,
                insight_type='budget_trend',
                title='Your Average Purchase',
                description=f'Your average purchase amount is ${avg_spending:.2f}',
                data={'average': float(avg_spending)}
            )

        # Category preference insight
        category_count = {}
        for interaction in interactions:
            if interaction.clicked_products.exists():
                for product in interaction.clicked_products.all():
                    category_count[product.category] = category_count.get(product.category, 0) + 1

        if category_count:
            top_category = max(category_count, key=category_count.get)
            UserInsight.objects.create(
                user=user,
                insight_type='category_preference',
                title=f'Interested in {top_category}s',
                description=f'You\'ve shown interest in {top_category} products {category_count[top_category]} times',
                data={'category': top_category, 'count': category_count[top_category]}
            )

        return JsonResponse({'success': True, 'message': 'Insights generated'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
