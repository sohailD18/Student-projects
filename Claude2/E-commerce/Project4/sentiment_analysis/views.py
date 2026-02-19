from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
import json
from .models import Review


def index(request):
    """
    Render the review submission form page.
    Requires authentication.
    """
    if not request.user.is_authenticated:
        return redirect('sentiment_analysis:login')
    return render(request, 'index.html')


def dashboard(request):
    """
    Render the analytics dashboard page.
    Requires authentication.
    """
    if not request.user.is_authenticated:
        return redirect('sentiment_analysis:login')
    return render(request, 'dashboard.html')


def login_view(request):
    """
    Render and handle login form.
    """
    if request.user.is_authenticated:
        return redirect('sentiment_analysis:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Debug output (remove in production)
        print(f"Login attempt - Username: {username}, Password length: {len(password) if password else 0}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('sentiment_analysis:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def register_view(request):
    """
    Render and handle registration form.
    """
    if request.user.is_authenticated:
        return redirect('sentiment_analysis:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not all([username, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('sentiment_analysis:login')

    return render(request, 'register.html')


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('sentiment_analysis:login')


@require_http_methods(["GET"])
def dashboard_api(request):
    """
    API endpoint to get dashboard statistics and data.
    """
    stats = Review.get_dashboard_stats()
    return JsonResponse(stats)


@csrf_exempt
@require_http_methods(["POST"])
def submit_review(request):
    """
    Handle review submission via AJAX.
    Automatically calculates sentiment before saving.
    Requires authentication.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required.'
        }, status=401)

    try:
        # Parse JSON data from request body
        data = json.loads(request.body)

        # Extract form data
        product_name = data.get('product_name')
        review_text = data.get('review_text')
        rating = data.get('rating')

        # Validate required fields
        if not all([product_name, review_text, rating]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required.'
            }, status=400)

        # Validate rating
        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                return JsonResponse({
                    'success': False,
                    'error': 'Rating must be between 1 and 5.'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid rating value.'
            }, status=400)

        # Create review (sentiment is calculated automatically in save method)
        review = Review.objects.create(
            user=request.user,
            product_name=product_name,
            review_text=review_text,
            rating=rating
        )

        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully!',
            'review': {
                'id': review.id,
                'product_name': review.get_product_name_display(),
                'review_text': review.review_text,
                'rating': review.rating,
                'sentiment': review.sentiment,
                'sentiment_score': review.sentiment_score,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data.'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def recent_reviews(request):
    """
    API endpoint to get recent reviews for the dashboard.
    """
    limit = request.GET.get('limit', 10)
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10

    reviews = list(Review.objects.all()[:limit].values(
        'id', 'product_name', 'review_text', 'rating',
        'sentiment', 'created_at'
    ))

    return JsonResponse({'reviews': reviews})
