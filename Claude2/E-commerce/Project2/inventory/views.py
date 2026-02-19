"""
Views for Inventory Management System

This module contains all view functions:
- Dashboard view (main page)
- API endpoints for forecasting
- Product management views
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Count
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
import json

from .models import Product, SalesData
from .utils import (
    generate_forecast,
    get_all_products_forecast,
    get_dashboard_stats,
    get_historical_sales_for_chart,
    calculate_trend_analysis,
    calculate_model_accuracy,
    get_sales_forecast_with_confidence,
    get_comprehensive_product_report
)


@login_required(login_url='/login/')
def dashboard(request):
    """
    Main Dashboard View

    Displays:
    - KPI cards (Total Products, Low Stock Alerts, etc.)
    - Charts (Sales trends, forecasts)
    - Inventory table with status indicators
    - Replenishment suggestions

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered dashboard template
    """
    # Get dashboard statistics
    stats = get_dashboard_stats()

    # Get all products with their forecasts
    products = Product.objects.all().order_by('name')

    # Get forecasts for all products
    forecasts = get_all_products_forecast()

    # Create a mapping of product_id to forecast
    forecast_map = {f['product_id']: f for f in forecasts}

    # Combine product data with forecast data
    products_with_forecasts = []
    for product in products:
        forecast = forecast_map.get(product.id, {})
        products_with_forecasts.append({
            'id': product.id,
            'name': product.name,
            'category': product.get_category_display(),
            'current_stock': product.current_stock,
            'price': float(product.price),
            'safety_stock': product.safety_stock,
            'predicted_demand': forecast.get('total_predicted_demand', 0),
            'average_daily_demand': forecast.get('average_daily_demand', 0),
            'suggested_order_quantity': forecast.get('suggested_order_quantity', 0),
            'status': forecast.get('status', 'good'),
            'status_display': forecast.get('status_display', 'Unknown'),
            'inventory_value': float(product.inventory_value),
        })

    # Pagination for inventory table
    paginator = Paginator(products_with_forecasts, 10)  # 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'stats': stats,
        'products': page_obj,
        'total_products': len(products_with_forecasts),
    }

    return render(request, 'dashboard.html', context)


def api_forecast_all(request):
    """
    API Endpoint: Get forecasts for all products

    Returns JSON with forecast data for all products.

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: JSON with all forecasts
    """
    forecasts = get_all_products_forecast()
    return JsonResponse({
        'success': True,
        'forecasts': forecasts,
        'total': len(forecasts)
    })


def api_forecast_product(request, product_id):
    """
    API Endpoint: Get forecast for a specific product

    Args:
        request: HTTP request object
        product_id: ID of the product

    Returns:
        JsonResponse: JSON with product forecast
    """
    forecast = generate_forecast(product_id)

    if 'error' in forecast:
        return JsonResponse({
            'success': False,
            'error': forecast['error']
        }, status=404)

    return JsonResponse({
        'success': True,
        'forecast': forecast
    })


def api_product_chart_data(request, product_id):
    """
    API Endpoint: Get chart data for a product

    Returns both historical sales data and forecast data
    for visualization in Chart.js.

    Args:
        request: HTTP request object
        product_id: ID of the product

    Returns:
        JsonResponse: JSON with historical and forecast data
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        }, status=404)

    # Get historical sales data
    historical = get_historical_sales_for_chart(product_id, days=90)

    # Get forecast data
    forecast = generate_forecast(product_id)

    return JsonResponse({
        'success': True,
        'product_name': product.name,
        'historical': historical,
        'forecast': forecast
    })


def api_dashboard_stats(request):
    """
    API Endpoint: Get dashboard statistics

    Returns real-time statistics for the dashboard KPI cards.

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: JSON with dashboard statistics
    """
    stats = get_dashboard_stats()
    return JsonResponse({
        'success': True,
        'stats': stats
    })


def api_products_list(request):
    """
    API Endpoint: Get list of all products

    Returns a paginated list of products with basic information.

    Query Parameters:
        page: Page number (default: 1)
        category: Filter by category (optional)
        search: Search by name (optional)
        status: Filter by stock status (optional)

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: JSON with products list
    """
    products = Product.objects.all()

    # Apply filters
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category=category_filter)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    products_data = []
    for product in page_obj:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'category': product.get_category_display(),
            'current_stock': product.current_stock,
            'price': float(product.price),
            'safety_stock': product.safety_stock,
        })

    return JsonResponse({
        'success': True,
        'products': products_data,
        'page': page_number,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count,
    })


def api_sales_data(request, product_id):
    """
    API Endpoint: Get sales data for a product

    Returns historical sales data for the specified product.

    Query Parameters:
        days: Number of days of data to return (default: 90)

    Args:
        request: HTTP request object
        product_id: ID of the product

    Returns:
        JsonResponse: JSON with sales data
    """
    days = int(request.GET.get('days', 90))
    sales_data = get_historical_sales_for_chart(product_id, days)

    return JsonResponse({
        'success': True,
        'product_id': product_id,
        'data': sales_data
    })


def api_inventory_summary(request):
    """
    API Endpoint: Get inventory summary

    Returns aggregated inventory data including:
    - Total inventory value
    - Stock status breakdown
    - Category distribution
    - Low stock items

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: JSON with inventory summary
    """
    products = Product.objects.all()

    # Calculate total inventory value
    total_value = sum(p.inventory_value for p in products)

    # Stock status breakdown
    forecasts = get_all_products_forecast()
    status_counts = {'low': 0, 'good': 0, 'overstock': 0, 'critical': 0, 'out_of_stock': 0}

    for f in forecasts:
        status = f.get('status', 'good')
        if status in status_counts:
            status_counts[status] += 1

    # Low stock items
    low_stock_items = [
        f for f in forecasts
        if f.get('status') in ['low', 'critical', 'out_of_stock']
    ][:10]  # Top 10

    # Category distribution
    category_distribution = {}
    for product in products:
        category = product.get_category_display()
        category_distribution[category] = category_distribution.get(category, 0) + 1

    return JsonResponse({
        'success': True,
        'summary': {
            'total_inventory_value': float(total_value),
            'total_products': products.count(),
            'status_counts': status_counts,
            'category_distribution': category_distribution,
            'low_stock_items': low_stock_items
        }
    })


def api_replenishment_report(request):
    """
    API Endpoint: Get replenishment report

    Returns a report of items that need to be reordered,
    with suggested order quantities.

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: JSON with replenishment report
    """
    forecasts = get_all_products_forecast()

    # Filter items that need replenishment
    needs_reorder = [
        f for f in forecasts
        if f.get('suggested_order_quantity', 0) > 0
    ]

    # Sort by suggested order quantity (descending)
    needs_reorder.sort(key=lambda x: x.get('suggested_order_quantity', 0), reverse=True)

    return JsonResponse({
        'success': True,
        'report': needs_reorder,
        'summary': {
            'total_items_to_reorder': len(needs_reorder),
            'total_units_needed': sum(f.get('suggested_order_quantity', 0) for f in needs_reorder),
            'estimated_cost': sum(
                f.get('suggested_order_quantity', 0) * 25  # Approximate price
                for f in needs_reorder
            )
        }
    })


def health_check(request):
    """
    Health check endpoint for monitoring

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: Health status
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected'
    })


def api_trend_analysis(request, product_id):
    """
    API Endpoint: Get trend analysis for a product

    Returns detailed trend analysis including:
    - Growth rate
    - Trend direction
    - Volatility
    - Seasonal patterns
    - Momentum

    Args:
        request: HTTP request object
        product_id: ID of the product

    Returns:
        JsonResponse: JSON with trend analysis
    """
    days = int(request.GET.get('days', 90))
    trend_data = calculate_trend_analysis(product_id, days)

    return JsonResponse({
        'success': True,
        'product_id': product_id,
        'analysis': trend_data
    })


def api_model_accuracy(request, product_id):
    """
    API Endpoint: Get model accuracy metrics

    Returns accuracy metrics for the forecasting model including:
    - MAPE (Mean Absolute Percentage Error)
    - RMSE (Root Mean Square Error)
    - MAE (Mean Absolute Error)
    - R-squared score
    - Accuracy level

    Args:
        request: HTTP request object
        product_id: ID of the product

    Returns:
        JsonResponse: JSON with accuracy metrics
    """
    accuracy_data = calculate_model_accuracy(product_id)

    return JsonResponse({
        'success': True,
        'product_id': product_id,
        'accuracy': accuracy_data
    })


def api_forecast_with_confidence(request, product_id):
    """
    API Endpoint: Get forecast with confidence intervals

    Returns forecast with upper and lower bounds for predictions.

    Query Parameters:
        days: Number of days to forecast (default: 30)

    Args:
        request: HTTP request object
        product_id: ID of the product

    Returns:
        JsonResponse: JSON with forecast and confidence intervals
    """
    days = int(request.GET.get('days', 30))
    forecast_data = get_sales_forecast_with_confidence(product_id, days)

    return JsonResponse({
        'success': True,
        'product_id': product_id,
        'forecast': forecast_data
    })


def api_comprehensive_report(request, product_id):
    """
    API Endpoint: Get comprehensive product report

    Returns a complete report combining:
    - Product information
    - Forecast with confidence intervals
    - Trend analysis
    - Model accuracy
    - Historical data

    Args:
        request: HTTP request object
        product_id: ID of the product

    Returns:
        JsonResponse: JSON with comprehensive report
    """
    report = get_comprehensive_product_report(product_id)

    return JsonResponse({
        'success': True,
        'report': report
    })


def api_all_trends(request):
    """
    API Endpoint: Get trend analysis for all products

    Returns trend analysis summary for all products.

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: JSON with all trend analyses
    """
    from .models import Product

    products = Product.objects.all()
    trends = []

    for product in products:
        trend_data = calculate_trend_analysis(product.id)
        if 'error' not in trend_data:
            trends.append({
                'product_id': product.id,
                'product_name': product.name,
                'category': product.get_category_display(),
                'trend_direction': trend_data['trend_direction'],
                'trend_display': trend_data['trend_display'],
                'growth_rate': trend_data['growth_rate'],
                'volatility': trend_data['volatility'],
                'momentum': trend_data['momentum']
            })

    return JsonResponse({
        'success': True,
        'trends': trends,
        'total': len(trends)
    })
