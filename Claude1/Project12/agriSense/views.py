from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .utils import (
    predict_yield, recommend_crops, analyze_yield_trends,
    get_top_performing_crops, assess_pest_risk, suggest_fertilizer
)
from .models import Crop, Season, YieldRecord


@csrf_exempt
@require_http_methods(["GET", "POST"])
def yield_prediction(request):
    """
    API endpoint for yield prediction.
    GET: Returns prediction form/documentation
    POST: Accepts crop_name and area_acres, returns prediction
    """
    if request.method == 'GET':
        return JsonResponse({
            'endpoint': '/api/yield-prediction/',
            'method': 'POST',
            'description': 'Predict crop yield based on area',
            'parameters': {
                'crop_name': 'string (e.g., "Wheat", "Rice")',
                'area_acres': 'number (e.g., 10.5)'
            },
            'example': {
                'crop_name': 'Wheat',
                'area_acres': 5
            },
            'available_crops': list(Crop.objects.values_list('name', flat=True))
        })

    # Handle POST request
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)

    crop_name = data.get('crop_name')
    area_acres = data.get('area_acres')

    # Validate inputs
    if not crop_name:
        return JsonResponse({
            'error': 'crop_name is required'
        }, status=400)

    if area_acres is None:
        return JsonResponse({
            'error': 'area_acres is required'
        }, status=400)

    try:
        area_acres = float(area_acres)
        if area_acres <= 0:
            raise ValueError('Area must be positive')
    except (ValueError, TypeError):
        return JsonResponse({
            'error': 'area_acres must be a positive number'
        }, status=400)

    # Get prediction
    result = predict_yield(crop_name, area_acres)

    if 'error' in result:
        return JsonResponse(result, status=404)

    return JsonResponse(result, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def crop_recommendations(request):
    """
    API endpoint for crop recommendations.
    Query params: soil_type (optional), season (optional)
    """
    soil_type = request.GET.get('soil_type')
    season = request.GET.get('season')

    results = recommend_crops(soil_type=soil_type, season=season)

    return JsonResponse({
        'filters': {
            'soil_type': soil_type,
            'season': season
        },
        'count': len(results),
        'recommendations': results
    }, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def yield_analysis(request):
    """
    API endpoint for yield trend analysis.
    Query params: crop_name (required)
    """
    crop_name = request.GET.get('crop_name')

    if not crop_name:
        return JsonResponse({
            'error': 'crop_name query parameter is required'
        }, status=400)

    result = analyze_yield_trends(crop_name)

    if 'error' in result:
        return JsonResponse(result, status=404)

    return JsonResponse(result, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def top_crops(request):
    """
    API endpoint for top performing crops.
    Query params: limit (optional, default=5)
    """
    limit = request.GET.get('limit', 5)

    try:
        limit = int(limit)
        if limit < 1 or limit > 50:
            limit = 5
    except ValueError:
        limit = 5

    results = get_top_performing_crops(limit=limit)

    return JsonResponse({
        'limit': limit,
        'count': len(results),
        'top_crops': results
    }, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def yield_chart_data(request):
    """
    API endpoint for yield chart data.
    Returns yield data for the last 5 years for all crops.
    """
    from django.db.models import Avg
    from collections import defaultdict

    # Get the last 5 years from yield records
    years = list(YieldRecord.objects.values_list('year', flat=True).distinct().order_by('-year')[:5])
    years.sort()  # Sort ascending for the chart

    # Get average yield by year
    yearly_data = []
    for year in years:
        avg_yield = YieldRecord.objects.filter(year=year).aggregate(avg=Avg('quantity'))['avg']
        yearly_data.append(round(avg_yield, 2) if avg_yield else 0)

    # Get top 5 crops with their yields by year
    top_crops_data = get_top_performing_crops(limit=5)
    crop_datasets = []

    colors = [
        'rgba(45, 90, 39, 0.8)',    # primary-green
        'rgba(74, 124, 67, 0.8)',   # secondary-green
        'rgba(139, 195, 74, 0.8)',  # light-green
        'rgba(141, 110, 99, 0.8)',  # earth-brown
        'rgba(255, 213, 79, 0.8)'   # yellow
    ]

    for idx, crop in enumerate(top_crops_data):
        crop_yields = []
        for year in years:
            try:
                record = YieldRecord.objects.filter(crop__name=crop['name'], year=year).first()
                crop_yields.append(round(record.quantity, 2) if record else 0)
            except:
                crop_yields.append(0)

        crop_datasets.append({
            'label': crop['name'],
            'data': crop_yields,
            'backgroundColor': colors[idx % len(colors)],
            'borderColor': colors[idx % len(colors)].replace('0.8', '1'),
            'borderWidth': 2
        })

    return JsonResponse({
        'years': years,
        'yearly_averages': yearly_data,
        'crop_datasets': crop_datasets
    }, status=200)


def dashboard_home(request):
    """Render main dashboard page"""
    context = {
        'total_crops': Crop.objects.count(),
        'total_seasons': Season.objects.count(),
        'total_yield_records': YieldRecord.objects.count(),
        'top_crops': get_top_performing_crops(limit=3)
    }
    return render(request, 'agriSense/dashboard.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def pest_risk_assessment(request):
    """
    API endpoint for pest risk assessment.
    Query params: season (required)
    """
    season = request.GET.get('season')

    if not season:
        return JsonResponse({
            'error': 'season query parameter is required',
            'available_seasons': list(Season.objects.values_list('name', flat=True))
        }, status=400)

    result = assess_pest_risk(season)

    return JsonResponse(result, status=200)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def fertilizer_recommendation(request):
    """
    API endpoint for fertilizer recommendations.
    GET: Returns documentation
    POST: Accepts crop_name, returns fertilizer schedule
    """
    if request.method == 'GET':
        return JsonResponse({
            'endpoint': '/api/fertilizer-recommendation/',
            'method': 'POST',
            'description': 'Get fertilizer schedule for a crop',
            'parameters': {
                'crop_name': 'string (e.g., "Wheat", "Rice", "Tomato")'
            },
            'example': {
                'crop_name': 'Wheat'
            },
            'available_crops': list(Crop.objects.values_list('name', flat=True))
        })

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)

    crop_name = data.get('crop_name')

    if not crop_name:
        return JsonResponse({
            'error': 'crop_name is required'
        }, status=400)

    result = suggest_fertilizer(crop_name)

    return JsonResponse(result, status=200)


def crop_planner(request):
    """Render crop planner page with form"""
    context = {
        'crops': Crop.objects.all(),
        'seasons': Season.objects.all(),
        'soil_types': Crop.SOIL_TYPE_CHOICES
    }
    return render(request, 'agriSense/crop_planner.html', context)


def yield_predictor(request):
    """Render yield predictor page with form"""
    context = {
        'crops': Crop.objects.all()
    }
    return render(request, 'agriSense/yield_predictor.html', context)


def analytics_reports(request):
    """Render analytics and reports page"""
    context = {
        'crops': Crop.objects.all(),
        'seasons': Season.objects.all(),
        'top_crops': get_top_performing_crops(limit=5)
    }
    return render(request, 'agriSense/reports.html', context)
