from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count, F, DecimalField
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Product, SalesHistory, CompetitorPrice, PriceHistory
from .services.pricing_algorithm import DynamicPricingEngine
from .forms import CustomUserCreationForm, CustomLoginForm


@login_required
def dashboard(request):
    """Dashboard view with KPI cards and revenue chart."""
    # Calculate KPIs
    total_products = Product.objects.count()

    # Total revenue from all sales
    sales_revenue = SalesHistory.objects.aggregate(
        total=Sum(F('quantity_sold') * F('sale_price'))
    )['total'] or 0

    # Total sales count
    total_sales_count = SalesHistory.objects.aggregate(
        total=Sum('quantity_sold')
    )['total'] or 0

    # Calculate average margin across all products
    products = Product.objects.all()
    if products.exists():
        avg_margin = sum(p.margin for p in products) / products.count()
    else:
        avg_margin = 0

    # Get revenue and cost data for the chart (last 90 days)
    cutoff_date = timezone.now() - timedelta(days=90)

    # Get daily revenue
    daily_revenue = SalesHistory.objects.filter(
        date__gte=cutoff_date
    ).annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        revenue=Sum(F('quantity_sold') * F('sale_price'))
    ).order_by('day')

    # Get daily cost (sum of base_cost * quantity_sold)
    daily_cost = []
    for item in daily_revenue:
        # Get sales for this day
        day_sales = SalesHistory.objects.filter(
            date__date=item['day']
        )
        cost = sum(
            sale.quantity_sold * sale.product.base_cost
            for sale in day_sales
        )
        daily_cost.append({
            'day': item['day'],
            'cost': cost
        })

    # Prepare chart data
    chart_labels = [str(item['day'].strftime('%Y-%m-%d')) for item in daily_revenue]
    chart_revenue = [float(item['revenue'] or 0) for item in daily_revenue]
    chart_costs = [float(item['cost']) for item in daily_cost]

    # Calculate profit margin for chart
    chart_profit = [revenue - cost for revenue, cost in zip(chart_revenue, chart_costs)]

    context = {
        'total_revenue': sales_revenue,
        'total_sales': total_sales_count,
        'avg_margin': round(avg_margin, 2),
        'total_products': total_products,
        'chart_labels': chart_labels,
        'chart_revenue': chart_revenue,
        'chart_costs': chart_costs,
        'chart_profit': chart_profit,
    }
    return render(request, 'pricing_engine/dashboard.html', context)


@login_required
def product_list(request):
    """Product list view with table of all products."""
    products = Product.objects.all()

    context = {
        'products': products,
    }
    return render(request, 'pricing_engine/product_list.html', context)


@login_required
def product_detail(request, product_id):
    """Product detail view with sales history and competitor charts."""
    product = get_object_or_404(Product, id=product_id)

    # Get sales history for chart (last 90 days)
    cutoff_date = timezone.now() - timedelta(days=90)
    sales_history = product.sales_history.filter(date__gte=cutoff_date).order_by('date')

    # Get competitor prices
    competitor_prices = product.competitor_prices.all().order_by('-recorded_at')[:10]

    # Prepare sales chart data
    sales_labels = [str(sale.date.strftime('%Y-%m-%d')) for sale in sales_history]
    sales_quantities = [sale.quantity_sold for sale in sales_history]
    sales_prices = [float(sale.sale_price) for sale in sales_history]

    # Prepare competitor chart data
    competitor_labels = [str(cp.recorded_at.strftime('%Y-%m-%d')) for cp in competitor_prices]
    competitor_prices_list = [float(cp.price) for cp in competitor_prices]

    # Get recent price changes
    price_history = product.price_history.all()[:10]

    context = {
        'product': product,
        'sales_history': sales_history,
        'competitor_prices': competitor_prices,
        'price_history': price_history,
        'sales_labels': sales_labels,
        'sales_quantities': sales_quantities,
        'sales_prices': sales_prices,
        'competitor_labels': competitor_labels,
        'competitor_prices_list': competitor_prices_list,
    }
    return render(request, 'pricing_engine/product_detail.html', context)


@login_required
def simulation(request):
    """Simulation view for testing hypothetical pricing scenarios."""
    products = Product.objects.all()

    context = {
        'products': products,
    }
    return render(request, 'pricing_engine/simulation.html', context)


@login_required
def run_ai_analysis(request, product_id):
    """Run AI pricing analysis and redirect to product detail."""
    product = get_object_or_404(Product, id=product_id)

    # Run the pricing engine
    engine = DynamicPricingEngine()
    suggested_price, reason = engine.calculate_optimal_price(product)

    # Store the suggestion in session for display
    request.session['suggested_price'] = str(suggested_price)
    request.session['price_reason'] = reason
    request.session['product_id'] = product_id

    messages.success(request, f'AI Analysis complete! Suggested price: ${suggested_price}')

    return redirect('pricing_engine:product_detail', product_id=product_id)


@login_required
def api_update_price(request, product_id):
    """API endpoint to update price using AI recommendation."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'})

    product = get_object_or_404(Product, id=product_id)

    try:
        # Get the suggested price from session or recalculate
        if 'suggested_price' in request.session:
            new_price = Decimal(request.session['suggested_price'])
            reason = request.session.get('price_reason', 'AI Optimization')
        else:
            engine = DynamicPricingEngine()
            new_price, reason = engine.calculate_optimal_price(product)

        old_price = product.current_price

        # Update product price
        product.current_price = new_price
        product.save()

        # Log to price history
        PriceHistory.objects.create(
            product=product,
            old_price=old_price,
            new_price=new_price,
            reason=reason
        )

        # Clear session
        request.session.pop('suggested_price', None)
        request.session.pop('price_reason', None)
        request.session.pop('product_id', None)

        return JsonResponse({
            'success': True,
            'old_price': str(old_price),
            'new_price': str(new_price),
            'reason': reason,
            'message': f'Price updated from ${old_price} to ${new_price}'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def api_simulate(request):
    """API endpoint for AJAX simulation."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'})

    product_id = request.POST.get('product_id')
    hypothetical_price = request.POST.get('hypothetical_price')
    hypothetical_demand = request.POST.get('hypothetical_demand')

    try:
        product = get_object_or_404(Product, id=product_id)
        hypothetical_price = Decimal(hypothetical_price)
        hypothetical_demand = int(hypothetical_demand)

        # Run simulation
        engine = DynamicPricingEngine()
        results = engine.simulate_profit(product, hypothetical_price, hypothetical_demand)

        return JsonResponse({
            'success': True,
            'results': results
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def api_get_ai_suggestion(request, product_id):
    """API endpoint to get AI price suggestion without updating."""
    product = get_object_or_404(Product, id=product_id)

    try:
        engine = DynamicPricingEngine()
        suggested_price, reason = engine.calculate_optimal_price(product)

        return JsonResponse({
            'success': True,
            'current_price': str(product.current_price),
            'suggested_price': str(suggested_price),
            'reason': reason,
            'price_difference': str(suggested_price - product.current_price),
            'percent_change': float(((suggested_price - product.current_price) / product.current_price) * 100)
            if product.current_price > 0 else 0
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# ==================== Authentication Views ====================

def user_register(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('pricing_engine:dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('pricing_engine:user_login')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
    }
    return render(request, 'pricing_engine/register.html', context)


def user_login(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('pricing_engine:dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to next page if specified, otherwise dashboard
            next_page = request.GET.get('next', '')
            if next_page:
                return redirect(next_page)
            return redirect('pricing_engine:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    context = {
        'form': form,
    }
    return render(request, 'pricing_engine/login.html', context)


def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('pricing_engine:user_login')


@login_required
def user_profile(request):
    """
    User profile view.
    """
    from django.utils import timezone
    import datetime

    # Calculate days since user joined
    days_since_joined = (timezone.now() - request.user.date_joined).days

    context = {
        'user': request.user,
        'days_since_joined': days_since_joined,
    }
    return render(request, 'pricing_engine/profile.html', context)
