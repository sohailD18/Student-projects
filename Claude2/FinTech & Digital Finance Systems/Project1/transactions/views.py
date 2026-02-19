"""
Django views for the fraud detection system.
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Avg, Q, F, FloatField
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
from collections import defaultdict

from .models import Transaction, ModelMetrics, FraudAlert, AuditLog
from .ml_engine import get_model, get_fraud_reasons


def home(request):
    """
    Home page - redirect to dashboard
    """
    return render(request, 'transactions/home.html')


def dashboard(request):
    """
    Main dashboard with fraud statistics and visualizations.
    """
    # Get summary statistics
    total_transactions = Transaction.objects.count()
    total_fraud = Transaction.objects.filter(is_fraud=True).count()
    total_flagged = Transaction.objects.filter(is_flagged=True).count()

    # Calculate fraud rate
    fraud_rate = (total_fraud / total_transactions * 100) if total_transactions > 0 else 0

    # Get recent fraud alerts
    recent_alerts = FraudAlert.objects.select_related('transaction').order_by('-created_at')[:10]

    # Get recent transactions
    recent_transactions = Transaction.objects.order_by('-timestamp')[:10]

    # Get top risky merchants
    risky_merchants = Transaction.objects.filter(is_fraud=True).values('merchant').annotate(
        fraud_count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('-fraud_count')[:10]

    # Get fraud by country
    fraud_by_country = Transaction.objects.filter(is_fraud=True).values('country').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Get fraud by category
    fraud_by_category = list(Transaction.objects.filter(is_fraud=True).values('merchant_category').annotate(
        count=Count('id')
    ).order_by('-count'))

    context = {
        'total_transactions': total_transactions,
        'total_fraud': total_fraud,
        'total_flagged': total_flagged,
        'fraud_rate': round(fraud_rate, 2),
        'recent_alerts': recent_alerts,
        'recent_transactions': recent_transactions,
        'risky_merchants': risky_merchants,
        'fraud_by_country': fraud_by_country,
        'fraud_by_category': json.dumps(fraud_by_category),
    }

    return render(request, 'transactions/dashboard.html', context)


def dashboard_api_data(request):
    """
    API endpoint to provide data for dashboard charts.
    """
    # Date range for charts (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    # Transaction trend over time
    transaction_trend = Transaction.objects.filter(
        timestamp__gte=start_date
    ).annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        total=Count('id'),
        fraud=Count('id', filter=Q(is_fraud=True))
    ).order_by('date')

    # Risk score distribution
    risk_distribution = []
    for threshold in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        count = Transaction.objects.filter(
            risk_score__gte=threshold,
            risk_score__lt=threshold + 0.2
        ).count()
        risk_distribution.append({
            'range': f'{threshold*100:.0f}-{(threshold+0.2)*100:.0f}%',
            'count': count
        })

    # Fraud by transaction type
    fraud_by_type = Transaction.objects.filter(is_fraud=True).values('transaction_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Hourly fraud pattern
    hourly_pattern = Transaction.objects.filter(
        timestamp__gte=start_date
    ).annotate(
        hour=TruncHour('timestamp')
    ).values('hour').annotate(
        total=Count('id'),
        fraud=Count('id', filter=Q(is_fraud=True))
    ).order_by('hour')

    data = {
        'transaction_trend': list(transaction_trend),
        'risk_distribution': risk_distribution,
        'fraud_by_type': list(fraud_by_type),
        'hourly_pattern': list(hourly_pattern),
    }

    return JsonResponse(data)


def transaction_list(request):
    """
    List all transactions with filtering and highlighting.
    """
    # Get filter parameters
    fraud_filter = request.GET.get('fraud', 'all')
    status_filter = request.GET.get('status', 'all')
    search = request.GET.get('search', '')

    # Build queryset
    transactions = Transaction.objects.all()

    # Apply filters
    if fraud_filter == 'fraud':
        transactions = transactions.filter(is_fraud=True)
    elif fraud_filter == 'legitimate':
        transactions = transactions.filter(is_fraud=False)

    if status_filter == 'flagged':
        transactions = transactions.filter(is_flagged=True)
    elif status_filter == 'reviewed':
        transactions = transactions.filter(is_reviewed=True)

    if search:
        transactions = transactions.filter(
            Q(transaction_id__icontains=search) |
            Q(merchant__icontains=search) |
            Q(account_id__icontains=search)
        )

    # Order by timestamp
    transactions = transactions.order_by('-timestamp')[:100]

    # Get statistics for filters
    stats = {
        'total': Transaction.objects.count(),
        'fraud': Transaction.objects.filter(is_fraud=True).count(),
        'flagged': Transaction.objects.filter(is_flagged=True).count(),
    }

    context = {
        'transactions': transactions,
        'stats': stats,
        'filters': {
            'fraud': fraud_filter,
            'status': status_filter,
            'search': search,
        }
    }

    return render(request, 'transactions/transaction_list.html', context)


def transaction_detail(request, transaction_id):
    """
    Detailed view of a single transaction.
    """
    transaction = Transaction.objects.get(transaction_id=transaction_id)
    alerts = transaction.alerts.all()

    context = {
        'transaction': transaction,
        'alerts': alerts,
    }

    return render(request, 'transactions/transaction_detail.html', context)


def model_performance(request):
    """
    Model performance monitoring page.
    """
    # Get latest model metrics
    latest_metrics = ModelMetrics.objects.order_by('-trained_at').first()

    # Get all metrics history
    metrics_history = ModelMetrics.objects.order_by('-trained_at')[:10]

    # Calculate current detection statistics
    total_transactions = Transaction.objects.count()
    total_fraud = Transaction.objects.filter(is_fraud=True).count()
    detected_fraud = Transaction.objects.filter(
        is_fraud=True,
        risk_score__gte=0.5
    ).count()

    # Calculate detection rate
    detection_rate = (detected_fraud / total_fraud * 100) if total_fraud > 0 else 0

    # Get model info
    model = get_model()
    model_info = {
        'is_trained': model.is_trained,
        'model_type': model.model_type,
        'version': model.version,
        'parameters': model.params,
    }

    context = {
        'latest_metrics': latest_metrics,
        'metrics_history': metrics_history,
        'total_transactions': total_transactions,
        'total_fraud': total_fraud,
        'detected_fraud': detected_fraud,
        'detection_rate': round(detection_rate, 2),
        'model_info': model_info,
    }

    return render(request, 'transactions/model_performance.html', context)


def fraud_analysis(request):
    """
    Fraud analysis and reporting page.
    """
    # Get all fraudulent transactions
    fraud_transactions = Transaction.objects.filter(
        is_fraud=True
    ).order_by('-timestamp')

    # Calculate fraud statistics
    total_fraud_amount = fraud_transactions.aggregate(
        total=Sum('amount')
    )['total'] or 0

    avg_fraud_amount = fraud_transactions.aggregate(
        avg=Avg('amount')
    )['avg'] or 0

    # Fraud by risk level
    fraud_by_risk = defaultdict(int)
    for transaction in fraud_transactions:
        risk_level = transaction.get_risk_level()
        fraud_by_risk[risk_level] += 1

    # Recent fraud trends
    end_date = timezone.now()
    start_dates = [
        end_date - timedelta(days=7),
        end_date - timedelta(days=30),
        end_date - timedelta(days=90),
    ]

    fraud_trends = []
    for start_date in start_dates:
        count = Transaction.objects.filter(
            is_fraud=True,
            timestamp__gte=start_date
        ).count()
        fraud_trends.append({
            'period': f"{(end_date - start_date).days} days",
            'count': count,
        })

    context = {
        'fraud_transactions': fraud_transactions[:50],
        'total_fraud_count': fraud_transactions.count(),
        'total_fraud_amount': total_fraud_amount,
        'avg_fraud_amount': avg_fraud_amount,
        'fraud_by_risk': dict(fraud_by_risk),
        'fraud_trends': fraud_trends,
    }

    return render(request, 'transactions/fraud_analysis.html', context)


def download_fraud_report(request):
    """
    Generate and download fraud report as CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fraud_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Transaction ID', 'Date', 'Amount', 'Merchant', 'Category',
        'Location', 'Country', 'Risk Score', 'Fraud Reason'
    ])

    fraud_transactions = Transaction.objects.filter(
        is_fraud=True
    ).order_by('-timestamp')

    for transaction in fraud_transactions:
        writer.writerow([
            transaction.transaction_id,
            transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            str(transaction.amount),
            transaction.merchant,
            transaction.merchant_category,
            transaction.location,
            transaction.country,
            f"{transaction.risk_score:.4f}",
            transaction.fraud_reason or 'N/A',
        ])

    return response


def api_predict_transaction(request):
    """
    API endpoint to predict fraud for a new transaction.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ['amount', 'transaction_type', 'merchant_category', 'country']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing field: {field}'}, status=400)

        # Get model
        model = get_model()

        if not model.is_trained:
            return JsonResponse({
                'error': 'Model not trained. Run train_model command first.'
            }, status=400)

        # Make prediction
        prediction = model.predict(data)
        prediction['fraud_reason'] = get_fraud_reasons(data, prediction['risk_score'])

        return JsonResponse(prediction)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_get_transaction_stats(request):
    """
    API endpoint to get transaction statistics.
    """
    stats = {
        'total_transactions': Transaction.objects.count(),
        'total_fraud': Transaction.objects.filter(is_fraud=True).count(),
        'total_flagged': Transaction.objects.filter(is_flagged=True).count(),
        'high_risk_count': Transaction.objects.filter(risk_score__gte=0.8).count(),
        'pending_review': Transaction.objects.filter(
            is_flagged=True,
            is_reviewed=False
        ).count(),
    }

    return JsonResponse(stats)


def api_recent_activity(request):
    """
    API endpoint to get recent transaction activity.
    """
    limit = int(request.GET.get('limit', 20))

    transactions = Transaction.objects.order_by('-timestamp')[:limit]

    data = []
    for t in transactions:
        data.append({
            'transaction_id': t.transaction_id,
            'amount': str(t.amount),
            'merchant': t.merchant,
            'timestamp': t.timestamp.isoformat(),
            'is_fraud': t.is_fraud,
            'risk_score': t.risk_score,
            'risk_level': t.get_risk_level(),
        })

    return JsonResponse({'transactions': data})
