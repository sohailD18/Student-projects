"""
Views for Carbon Credit Tracking System.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime
from .models import Industry, EmissionRecord, CarbonPrice
from .services import (
    predict_future_emissions,
    get_trading_suggestion,
    get_carbon_price_trend,
    analyze_industry_performance,
    log_prediction
)


def home(request):
    """
    Dashboard view with overview of all industries.
    """
    industries = Industry.objects.all()

    # Calculate overall statistics
    total_industries = industries.count()
    total_emissions = sum(industry.total_emissions for industry in industries)
    total_limits = sum(industry.emission_limit for industry in industries)
    active_credits = total_limits - total_emissions

    # Get latest carbon price
    latest_price = CarbonPrice.objects.order_by('-date').first()
    current_price = latest_price.price_per_ton if latest_price else 0

    context = {
        'industries': industries,
        'total_industries': total_industries,
        'total_emissions': round(total_emissions, 2),
        'active_credits': round(active_credits, 2),
        'current_price': round(current_price, 2),
        'page_title': 'Dashboard'
    }
    return render(request, 'dashboard.html', context)


def industry_detail(request, industry_id):
    """
    Detailed view for a specific industry with AI predictions.
    """
    try:
        industry = Industry.objects.get(id=industry_id)
    except Industry.DoesNotExist:
        return render(request, 'error.html', {'message': 'Industry not found'})

    # Get AI predictions
    prediction_result = predict_future_emissions(industry_id, months_to_predict=6)

    # Get trading suggestion for next month
    trading_suggestion = None
    if prediction_result.get('success') and prediction_result.get('predictions'):
        next_prediction = prediction_result['predictions'][0]
        trading_suggestion = get_trading_suggestion(
            next_prediction['predicted_emission'],
            industry.emission_limit,
            industry.total_emissions
        )

        # Log the prediction
        log_prediction(industry_id, prediction_result, trading_suggestion)

    # Get historical data for chart
    historical_data = EmissionRecord.objects.filter(
        industry=industry
    ).order_by('year', 'month')[:12]

    context = {
        'industry': industry,
        'prediction_result': prediction_result,
        'trading_suggestion': trading_suggestion,
        'historical_data': historical_data,
        'page_title': f'{industry.name} - Analysis'
    }
    return render(request, 'analysis.html', context)


def api_emission_data(request):
    """
    API endpoint returning emission data for charts.
    """
    industries = Industry.objects.all()

    data = {
        'labels': [],
        'datasets': []
    }

    # Get labels (months)
    records = EmissionRecord.objects.filter(
        year=timezone.now().year
    ).order_by('month')

    months_map = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    data['labels'] = [months_map[r.month] for r in records.distinct('month').order_by('month')]

    # Get data for each industry
    colors = [
        'rgba(54, 162, 235, 1)',
        'rgba(255, 99, 132, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(153, 102, 255, 1)'
    ]

    bg_colors = [
        'rgba(54, 162, 235, 0.2)',
        'rgba(255, 99, 132, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(255, 206, 86, 0.2)',
        'rgba(153, 102, 255, 0.2)'
    ]

    for idx, industry in enumerate(industries):
        emissions = EmissionRecord.objects.filter(
            industry=industry,
            year=timezone.now().year
        ).order_by('month')

        dataset = {
            'label': industry.name,
            'data': [float(e.emission_amount) for e in emissions],
            'borderColor': colors[idx % len(colors)],
            'backgroundColor': bg_colors[idx % len(bg_colors)],
            'borderWidth': 2
        }
        data['datasets'].append(dataset)

    return JsonResponse(data)


def api_predictions(request, industry_id):
    """
    API endpoint returning AI predictions for a specific industry.
    """
    prediction_result = predict_future_emissions(industry_id, months_to_predict=6)

    if not prediction_result.get('success'):
        return JsonResponse({
            'success': False,
            'error': prediction_result.get('error', 'Prediction failed')
        })

    industry = Industry.objects.get(id=industry_id)

    # Prepare historical data
    historical = EmissionRecord.objects.filter(
        industry=industry
    ).order_by('year', '-month')[:6]

    months_map = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    historical_labels = [f"{months_map[r.month]} {r.year}" for r in list(reversed(historical))]
    historical_data = [float(r.emission_amount) for r in list(reversed(historical))]

    # Prepare prediction data
    prediction_labels = [f"{months_map[p['month']]} {p['year']}" for p in prediction_result['predictions']]
    prediction_data = [p['predicted_emission'] for p in prediction_result['predictions']]

    # Get trading suggestion
    trading_suggestion = get_trading_suggestion(
        prediction_result['predictions'][0]['predicted_emission'],
        industry.emission_limit,
        industry.total_emissions
    )

    return JsonResponse({
        'success': True,
        'historical': {
            'labels': historical_labels,
            'data': historical_data
        },
        'predictions': {
            'labels': prediction_labels,
            'data': prediction_data
        },
        'trading_suggestion': trading_suggestion,
        'confidence_score': prediction_result.get('confidence_score', 0)
    })


def api_carbon_prices(request):
    """
    API endpoint returning carbon price data.
    """
    days = int(request.GET.get('days', 30))

    prices = CarbonPrice.objects.order_by('-date')[:days]

    data = {
        'labels': [p.date.strftime('%Y-%m-%d') for p in reversed(prices)],
        'data': [float(p.price_per_ton) for p in reversed(prices)]
    }

    return JsonResponse(data)


def api_price_analysis(request):
    """
    API endpoint returning carbon price trend analysis.
    """
    analysis = get_carbon_price_trend(days=30)
    return JsonResponse(analysis)


def api_industry_comparison(request):
    """
    API endpoint comparing performance across industries.
    """
    analysis = analyze_industry_performance()
    return JsonResponse(analysis)


def report(request):
    """
    View showing a printable summary report.
    """
    industries = Industry.objects.all()

    # Calculate statistics
    total_industries = industries.count()
    total_emissions = sum(industry.total_emissions for industry in industries)
    total_limits = sum(industry.emission_limit for industry in industries)

    # Get price analysis
    price_analysis = get_carbon_price_trend(days=30)

    # Get industry comparison
    performance = analyze_industry_performance()

    context = {
        'industries': industries,
        'total_industries': total_industries,
        'total_emissions': round(total_emissions, 2),
        'total_limits': round(total_limits, 2),
        'overall_surplus': round(total_limits - total_emissions, 2),
        'price_analysis': price_analysis,
        'performance': performance,
        'report_date': timezone.now(),
        'page_title': 'Carbon Credit Analysis Report'
    }
    return render(request, 'report.html', context)


def industry_predictions_api(request):
    """
    API endpoint for all industry predictions.
    """
    industries = Industry.objects.all()
    predictions_data = []

    for industry in industries:
        result = predict_future_emissions(industry.id, months_to_predict=3)

        if result.get('success'):
            trading = get_trading_suggestion(
                result['predictions'][0]['predicted_emission'],
                industry.emission_limit,
                industry.total_emissions
            )

            predictions_data.append({
                'industry_id': industry.id,
                'industry_name': industry.name,
                'industry_type': industry.industry_type,
                'current_emissions': round(industry.total_emissions, 2),
                'emission_limit': industry.emission_limit,
                'suggestion': trading['suggestion'],
                'urgency': trading['urgency'],
                'predicted_next_month': result['predictions'][0]['predicted_emission'],
                'confidence_score': result.get('confidence_score', 0)
            })

    return JsonResponse({'predictions': predictions_data})
