"""
Django views for the Inventory Management System.
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Q, F, Count, Case, When, IntegerField
from django.db.models.functions import Coalesce
from django.contrib import messages
from .models import Product, SalesRecord, InventoryPrediction
from .services.predictor import DemandPredictor


def dashboard(request):
    """
    Main dashboard view showing inventory overview with predictions.
    """
    # Get all products with their latest predictions
    products_with_predictions = []

    for product in Product.objects.all():
        latest_prediction = product.predictions.first()

        product_data = {
            'id': product.id,
            'name': product.name,
            'category': product.get_category_display(),
            'current_stock': product.current_stock,
            'unit_price': float(product.unit_price),
            'stock_value': product.stock_value,
        }

        if latest_prediction:
            product_data.update({
                'predicted_demand': latest_prediction.predicted_demand,
                'recommended_stock': latest_prediction.recommended_stock,
                'status': latest_prediction.get_status_display(),
                'status_code': latest_prediction.status,
                'confidence': latest_prediction.confidence_score,
                'prediction_date': latest_prediction.date_of_prediction,
            })
        else:
            product_data.update({
                'predicted_demand': None,
                'recommended_stock': None,
                'status': 'No Prediction',
                'status_code': 'none',
                'confidence': None,
                'prediction_date': None,
            })

        products_with_predictions.append(product_data)

    # Calculate summary statistics
    total_products = Product.objects.count()
    total_inventory_value = sum(p['stock_value'] for p in products_with_predictions)

    # Count status from predictions
    low_stock_count = sum(1 for p in products_with_predictions if p['status_code'] == 'low_stock')
    optimal_count = sum(1 for p in products_with_predictions if p['status_code'] == 'optimal')
    overstock_count = sum(1 for p in products_with_predictions if p['status_code'] == 'overstock')

    context = {
        'products': products_with_predictions,
        'total_products': total_products,
        'total_inventory_value': total_inventory_value,
        'low_stock_count': low_stock_count,
        'optimal_count': optimal_count,
        'overstock_count': overstock_count,
        'page_title': 'Dashboard',
    }

    return render(request, 'inventory_system/dashboard.html', context)


def analytics(request):
    """
    Analytics page with interactive charts for product demand prediction.
    """
    products = Product.objects.all()
    selected_product_id = request.GET.get('product')

    if selected_product_id:
        selected_product = get_object_or_404(Product, id=selected_product_id)
    else:
        selected_product = products.first()

    chart_data = None
    if selected_product:
        predictor = DemandPredictor()
        chart_data = predictor.get_historical_for_chart(selected_product)

    context = {
        'products': products,
        'selected_product': selected_product,
        'chart_data': chart_data,
        'page_title': 'Analytics',
    }

    return render(request, 'inventory_system/analytics.html', context)


def api_chart_data(request, product_id):
    """
    API endpoint to return chart data as JSON.
    Used by Chart.js for dynamic updates.
    """
    product = get_object_or_404(Product, id=product_id)
    predictor = DemandPredictor()
    chart_data = predictor.get_historical_for_chart(product)

    return JsonResponse(chart_data)


def reports(request):
    """
    Reports page showing products that need reordering.
    """
    # Get all products with low stock status
    low_stock_products = []

    for product in Product.objects.all():
        latest_prediction = product.predictions.first()

        if latest_prediction and latest_prediction.status == 'low_stock':
            low_stock_products.append({
                'id': product.id,
                'name': product.name,
                'category': product.get_category_display(),
                'current_stock': product.current_stock,
                'predicted_demand': latest_prediction.predicted_demand,
                'recommended_stock': latest_prediction.recommended_stock,
                'urgency': latest_prediction.recommended_stock - product.current_stock,
                'confidence': latest_prediction.confidence_score,
                'unit_price': float(product.unit_price),
                'order_value': float(product.unit_price) * latest_prediction.recommended_stock,
            })

    # Sort by urgency (most critical first)
    low_stock_products.sort(key=lambda x: x['urgency'], reverse=True)

    # Calculate total order value
    total_order_value = sum(p['order_value'] for p in low_stock_products)

    # Get products with overstock
    overstock_products = []

    for product in Product.objects.all():
        latest_prediction = product.predictions.first()

        if latest_prediction and latest_prediction.status == 'overstock':
            overstock_products.append({
                'id': product.id,
                'name': product.name,
                'current_stock': product.current_stock,
                'recommended_stock': latest_prediction.recommended_stock,
                'excess': product.current_stock - latest_prediction.recommended_stock,
                'excess_value': float(product.unit_price) * (
                    product.current_stock - latest_prediction.recommended_stock
                ),
            })

    # Sort by excess value
    overstock_products.sort(key=lambda x: x['excess_value'], reverse=True)

    total_excess_value = sum(p['excess_value'] for p in overstock_products)

    context = {
        'low_stock_products': low_stock_products,
        'overstock_products': overstock_products,
        'total_low_stock': len(low_stock_products),
        'total_overstock': len(overstock_products),
        'total_order_value': total_order_value,
        'total_excess_value': total_excess_value,
        'page_title': 'Reports',
    }

    return render(request, 'inventory_system/reports.html', context)


def product_detail(request, product_id):
    """
    Detailed view for a single product with all history and predictions.
    """
    product = get_object_or_404(Product, id=product_id)

    # Get latest prediction
    latest_prediction = product.predictions.first()

    # Get sales history (last 6 months)
    from django.utils import timezone
    from datetime import timedelta

    six_months_ago = timezone.now().date() - timedelta(days=180)
    sales_history = product.sales_records.filter(
        sale_date__gte=six_months_ago
    ).order_by('-sale_date')[:50]

    # Calculate statistics
    total_sales = product.sales_records.aggregate(
        total_quantity=Sum('quantity_sold'),
        total_revenue=Sum('revenue')
    )

    avg_monthly_sales = product.sales_records.filter(
        sale_date__gte=six_months_ago
    ).aggregate(
        avg_monthly=Sum('quantity_sold') / 6
    )

    context = {
        'product': product,
        'latest_prediction': latest_prediction,
        'sales_history': sales_history,
        'total_quantity_sold': total_sales['total_quantity'] or 0,
        'total_revenue': total_sales['total_revenue'] or 0,
        'avg_monthly_sales': avg_monthly_sales.get('avg_monthly', 0),
        'page_title': f'Product: {product.name}',
    }

    return render(request, 'inventory_system/product_detail.html', context)


def run_predictions_view(request):
    """
    View to trigger prediction generation from the web interface.
    """
    if request.method == 'POST':
        try:
            predictor = DemandPredictor()
            count = predictor.save_predictions()
            messages.success(request, f'Successfully generated {count} new predictions!')
        except Exception as e:
            messages.error(request, f'Error generating predictions: {str(e)}')

    # Get context data
    total_products = Product.objects.count()
    total_predictions = InventoryPrediction.objects.count()

    return render(request, 'inventory_system/run_predictions.html', {
        'page_title': 'Run Predictions',
        'total_products': total_products,
        'total_predictions': total_predictions,
    })
