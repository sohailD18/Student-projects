import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse
from .models import Product, Category
from .recommendations import (
    get_personalized_recommendations,
    get_similar_products,
    get_frequently_bought_together,
    refresh_recommendation_model
)


def home(request):
    """
    Dynamic homepage with AI-powered recommendations.

    Logic:
    - If user is logged in: Show personalized recommendations based on their
      past interactions (views, purchases, wishlist)
    - If user is anonymous: Show latest products across all categories

    Also displays:
    - Featured categories
    - Popular products (most purchased)
    """
    # Get all categories for the sidebar/navigation
    categories = Category.objects.all()

    # Initialize context variables
    personalized_recommendations = []
    latest_products = []
    popular_products = []
    frequently_bought = []

    if request.user.is_authenticated:
        # LOGGED IN USER: Get AI-powered personalized recommendations

        # Build recommendation model if needed
        refresh_recommendation_model()

        # Get personalized recommendations based on user's past interactions
        personalized_recommendations = get_personalized_recommendations(
            user_id=request.user.id,
            n=8
        )

        # If user has some interactions, also show "frequently bought together"
        # for their most recently viewed product
        from .models import UserInteraction

        last_viewed = UserInteraction.objects.filter(
            user=request.user,
            interaction_type='view'
        ).order_by('-timestamp').first()

        if last_viewed:
            frequently_bought = get_frequently_bought_together(
                product_id=last_viewed.product.id,
                n=4
            )

        # Get popular products as fallback (most purchased)
        popular_products = Product.objects.all()[:6]

    else:
        # ANONYMOUS USER: Show latest products
        latest_products = Product.objects.select_related('category').all()[:12]

        # Also show some popular products
        popular_products = Product.objects.all()[:6]

    # Get featured categories (categories with most products)
    from django.db.models import Count
    featured_categories = Category.objects.annotate(
        product_count=Count('products')
    ).filter(product_count__gt=0).order_by('-product_count')[:5]

    context = {
        'categories': categories,
        'featured_categories': featured_categories,
        'personalized_recommendations': personalized_recommendations,
        'latest_products': latest_products,
        'popular_products': popular_products,
        'frequently_bought': frequently_bought,
        'user_authenticated': request.user.is_authenticated,
    }

    return render(request, 'shop/home.html', context)


def product_detail(request, product_id):
    """
    Product detail page with AI-powered recommendations.

    Shows:
    - Product details
    - Similar products (content-based filtering)
    - Frequently bought together (collaborative filtering)
    """
    product = Product.objects.get(id=product_id)

    # Get similar products using content-based filtering
    similar_products = get_similar_products(product_id=product.id, n=4)

    # Get frequently bought together
    frequently_bought = get_frequently_bought_together(
        product_id=product.id,
        n=4
    )
    # Extract just the products from (product, score) tuples
    frequently_bought_products = [p for p, score in frequently_bought]

    context = {
        'product': product,
        'similar_products': similar_products,
        'frequently_bought': frequently_bought_products,
    }

    return render(request, 'shop/product_detail.html', context)


def category_products(request, category_id):
    """
    Page showing all products in a category with recommendations.
    """
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)

    # If user is logged in, show personalized recommendations
    recommendations = []
    if request.user.is_authenticated:
        recommendations = get_personalized_recommendations(
            user_id=request.user.id,
            n=4
        )

    context = {
        'category': category,
        'products': products,
        'recommendations': recommendations,
    }

    return render(request, 'shop/category.html', context)


@login_required
def dashboard(request):
    """
    User dashboard with personalized insights and recommendations.

    Shows:
    - User's recent interactions
    - Personalized recommendations
    - Recommended based on purchase history
    """
    from .models import UserInteraction

    # Get user's recent interactions
    recent_views = UserInteraction.objects.filter(
        user=request.user,
        interaction_type='view'
    ).select_related('product').order_by('-timestamp')[:5]

    recent_purchases = UserInteraction.objects.filter(
        user=request.user,
        interaction_type='purchase'
    ).select_related('product').order_by('-timestamp')[:5]

    # Get personalized recommendations
    recommendations = get_personalized_recommendations(
        user_id=request.user.id,
        n=8
    )

    # Get recommendations based on last purchase
    purchase_based_recommendations = []
    if recent_purchases:
        last_purchase = recent_purchases.first()
        purchase_based_recommendations = get_frequently_bought_together(
            product_id=last_purchase.product.id,
            n=4
        )

    context = {
        'recent_views': recent_views,
        'recent_purchases': recent_purchases,
        'recommendations': recommendations,
        'purchase_based_recommendations': purchase_based_recommendations,
    }

    return render(request, 'shop/dashboard.html', context)


@login_required
def analytics_dashboard(request):
    """
    Analytics dashboard showing key store metrics and insights.

    Displays:
    - Total views across all products
    - Total purchases
    - Top 5 most viewed products
    - Top 5 most purchased products
    - Recent activity timeline
    - Category breakdown
    """
    from .models import UserInteraction
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta

    # Basic stats
    total_views = UserInteraction.objects.filter(interaction_type='view').count()
    total_purchases = UserInteraction.objects.filter(interaction_type='purchase').count()
    total_cart_adds = UserInteraction.objects.filter(interaction_type='cart').count()
    total_wishlist_adds = UserInteraction.objects.filter(interaction_type='wishlist').count()

    # Top 5 most viewed products
    top_viewed_products = UserInteraction.objects.filter(
        interaction_type='view'
    ).values(
        'product__id',
        'product__name',
        'product__price',
        'product__category__name'
    ).annotate(
        view_count=Count('product__id')
    ).order_by('-view_count')[:5]

    # Top 5 most purchased products
    top_purchased_products = UserInteraction.objects.filter(
        interaction_type='purchase'
    ).values(
        'product__id',
        'product__name',
        'product__price',
        'product__category__name'
    ).annotate(
        purchase_count=Count('product__id')
    ).order_by('-purchase_count')[:5]

    # Category breakdown
    category_stats = UserInteraction.objects.filter(
        interaction_type='view'
    ).values(
        'product__category__name'
    ).annotate(
        views=Count('id')
    ).order_by('-views')

    # Recent activity (last 10 interactions)
    recent_activity = UserInteraction.objects.select_related(
        'user', 'product'
    ).order_by('-timestamp')[:10]

    # Stats for the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    views_last_7_days = UserInteraction.objects.filter(
        interaction_type='view',
        timestamp__gte=seven_days_ago
    ).count()

    purchases_last_7_days = UserInteraction.objects.filter(
        interaction_type='purchase',
        timestamp__gte=seven_days_ago
    ).count()

    # Calculate total revenue
    total_revenue = 0
    purchases = UserInteraction.objects.filter(interaction_type='purchase').select_related('product')
    for purchase in purchases:
        total_revenue += purchase.product.price

    # Unique users count
    unique_users = UserInteraction.objects.values('user').distinct().count()

    context = {
        # Basic stats
        'total_views': total_views,
        'total_purchases': total_purchases,
        'total_cart_adds': total_cart_adds,
        'total_wishlist_adds': total_wishlist_adds,
        'total_revenue': total_revenue,
        'unique_users': unique_users,
        # Top products
        'top_viewed_products': top_viewed_products,
        'top_purchased_products': top_purchased_products,
        # Category stats
        'category_stats': category_stats,
        # Recent activity
        'recent_activity': recent_activity,
        # Weekly stats
        'views_last_7_days': views_last_7_days,
        'purchases_last_7_days': purchases_last_7_days,
    }

    return render(request, 'shop/analytics.html', context)


@login_required
def export_interactions_csv(request):
    """
    Export all User Interactions to a CSV file for download.

    CSV columns:
    - User ID
    - Username
    - Product ID
    - Product Name
    - Category
    - Interaction Type
    - Timestamp
    - Price (at time of interaction)

    The response includes appropriate headers to trigger a file download.
    """
    from .models import UserInteraction

    # Create the HttpResponse object with CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="user_interactions_report.csv"'},
    )

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow([
        'User ID',
        'Username',
        'Product ID',
        'Product Name',
        'Category',
        'Price',
        'Interaction Type',
        'Timestamp'
    ])

    # Query all interactions with related data
    interactions = UserInteraction.objects.select_related(
        'user',
        'product',
        'product__category'
    ).order_by('-timestamp')

    # Write data rows
    for interaction in interactions:
        writer.writerow([
            interaction.user.id,
            interaction.user.username,
            interaction.product.id,
            interaction.product.name,
            interaction.product.category.name,
            str(interaction.product.price),
            interaction.get_interaction_type_display(),
            interaction.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


@login_required
def export_interactions_csv_filtered(request):
    """
    Export filtered User Interactions to CSV.

    Query parameters:
    - interaction_type: Filter by type (view, purchase, cart, wishlist)
    - start_date: Filter by start date (YYYY-MM-DD)
    - end_date: Filter by end date (YYYY-MM-DD)
    - user_id: Filter by specific user

    Example: /export/csv/?interaction_type=purchase&start_date=2026-01-01
    """
    from .models import UserInteraction
    from datetime import datetime

    # Create response
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="interactions_filtered.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow([
        'User ID',
        'Username',
        'Product ID',
        'Product Name',
        'Category',
        'Price',
        'Interaction Type',
        'Timestamp'
    ])

    # Build queryset with filters
    interactions = UserInteraction.objects.select_related(
        'user',
        'product',
        'product__category'
    )

    # Apply filters if provided
    interaction_type = request.GET.get('interaction_type')
    if interaction_type:
        interactions = interactions.filter(interaction_type=interaction_type)

    start_date = request.GET.get('start_date')
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            interactions = interactions.filter(timestamp__gte=start_dt)
        except ValueError:
            pass

    end_date = request.GET.get('end_date')
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            interactions = interactions.filter(timestamp__lte=end_dt)
        except ValueError:
            pass

    user_id = request.GET.get('user_id')
    if user_id and user_id.isdigit():
        interactions = interactions.filter(user_id=int(user_id))

    # Order and write data
    interactions = interactions.order_by('-timestamp')

    for interaction in interactions:
        writer.writerow([
            interaction.user.id,
            interaction.user.username,
            interaction.product.id,
            interaction.product.name,
            interaction.product.category.name,
            str(interaction.product.price),
            interaction.get_interaction_type_display(),
            interaction.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@login_required
@csrf_exempt
def track_interaction(request):
    """
    AJAX endpoint to track user interactions (cart, wishlist, purchase).

    Accepts POST requests with:
    - product_id: ID of the product
    - interaction_type: Type of interaction ('cart', 'wishlist', 'purchase')

    Returns JSON response with success status.
    """
    from .models import UserInteraction, Product

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST allowed'}, status=405)

    try:
        product_id = request.POST.get('product_id')
        interaction_type = request.POST.get('interaction_type')

        if not product_id or not interaction_type:
            return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)

        # Validate interaction type
        valid_types = ['cart', 'wishlist', 'purchase']
        if interaction_type not in valid_types:
            return JsonResponse({'success': False, 'error': 'Invalid interaction type'}, status=400)

        # Get product
        product = Product.objects.get(id=product_id)

        # Create interaction
        UserInteraction.objects.create(
            user=request.user,
            product=product,
            interaction_type=interaction_type
        )

        return JsonResponse({'success': True, 'message': f'{interaction_type} tracked successfully'})

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Custom Authentication Views


def custom_login(request):
    """
    Custom login page for users.
    """
    from django.contrib.auth import authenticate

    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to next page if provided, otherwise home
            next_url = request.GET.get('next', 'shop:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'shop/login.html')


def custom_register(request):
    """
    Custom registration page for new users.
    """
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('shop:home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'shop/register.html', {'form': form})


@login_required
def custom_logout(request):
    """
    Custom logout for users.
    """
    from django.contrib.auth import logout

    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop:home')
