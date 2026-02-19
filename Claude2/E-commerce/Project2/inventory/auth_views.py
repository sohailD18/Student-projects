"""
Authentication Views for Inventory Management System

Handles user registration, login, and logout.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def register_view(request):
    """
    User Registration View

    Handles new user registration with form validation.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Registration page or redirect
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        # Validation
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html')

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('inventory:login')

        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')

    return render(request, 'register.html')


def login_view(request):
    """
    User Login View

    Handles user authentication and login.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Login page or redirect
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect to next page or dashboard
            next_url = request.GET.get('next', reverse('inventory:dashboard'))
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def logout_view(request):
    """
    User Logout View

    Logs out the current user and redirects to login.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Redirect to login page
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('inventory:login')


@login_required
def profile_view(request):
    """
    User Profile View

    Displays user profile information.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Profile page
    """
    user = request.user

    # Get user's activity
    from inventory.models import Product, SalesData

    context = {
        'user': user,
        'total_products': Product.objects.count(),
        'total_sales_records': SalesData.objects.count(),
    }

    return render(request, 'profile.html', context)
