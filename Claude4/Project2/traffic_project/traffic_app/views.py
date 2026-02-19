"""
Views for Traffic Congestion Prediction System

This module contains all the view functions that handle HTTP requests and
return appropriate responses. It integrates with the ML model for predictions
and provides data for visualizations.

Key Views:
    - home: Dashboard with summary statistics
    - predict: Handles congestion prediction requests
    - analysis: Provides data for charts and analytics
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg, Q
from django.db import transaction
from django.utils import timezone

from .models import TrafficData


# ============================================================================
# ML MODEL LOADING
# ============================================================================

def load_ml_model():
    """
    Load the pre-trained ML model, encoders, and scaler.

    Returns:
        tuple: (model, label_encoders, scaler, feature_columns)

    Note:
        This function uses lazy loading - the model is loaded once and cached.
    """
    # Get the base directory of the project
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ml_models_dir = os.path.join(BASE_DIR, 'ml_models')

    try:
        import joblib

        # Load the trained Random Forest model
        model_path = os.path.join(ml_models_dir, 'traffic_model.pkl')
        model = joblib.load(model_path)

        # Load label encoders for categorical variables
        le_location = joblib.load(os.path.join(ml_models_dir, 'le_location.pkl'))
        le_weather = joblib.load(os.path.join(ml_models_dir, 'le_weather.pkl'))
        le_congestion = joblib.load(os.path.join(ml_models_dir, 'le_congestion.pkl'))

        # Load the scaler for numerical features
        scaler = joblib.load(os.path.join(ml_models_dir, 'scaler.pkl'))

        # Load feature columns information
        with open(os.path.join(ml_models_dir, 'feature_columns.json'), 'r') as f:
            feature_columns = json.load(f)

        return model, {
            'location': le_location,
            'weather': le_weather,
            'congestion': le_congestion
        }, scaler, feature_columns

    except Exception as e:
        print(f"Error loading ML model: {e}")
        return None, None, None, None


# Cache the loaded model
_model_cache = None
_encoders_cache = None
_scaler_cache = None
_features_cache = None


def get_model():
    """
    Get the cached ML model (lazy loading pattern).

    Returns:
        tuple: (model, encoders, scaler, feature_columns)
    """
    global _model_cache, _encoders_cache, _scaler_cache, _features_cache

    if _model_cache is None:
        _model_cache, _encoders_cache, _scaler_cache, _features_cache = load_ml_model()

    return _model_cache, _encoders_cache, _scaler_cache, _features_cache


# ============================================================================
# HOME / DASHBOARD VIEW
# ============================================================================

def home(request):
    """
    Render the home dashboard with summary statistics.

    Displays:
        - Total traffic records in database
        - Distribution of congestion levels
        - Recent high congestion hotspots
        - Quick navigation cards

    Args:
        request: HttpRequest object

    Returns:
        HttpResponse: Rendered home.html template
    """
    # Get total records
    total_records = TrafficData.objects.count()

    # Get congestion level distribution
    congestion_stats = TrafficData.objects.values('congestion_level').annotate(
        count=Count('id')
    )

    # Format congestion stats for template
    stats_dict = {stat['congestion_level']: stat['count'] for stat in congestion_stats}

    # Get recent high congestion locations (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    hotspots = TrafficData.objects.filter(
        date_time__gte=seven_days_ago,
        congestion_level='High'
    ).values('location').annotate(
        high_count=Count('id')
    ).order_by('-high_count')[:5]

    # Calculate average vehicle count
    avg_vehicles = TrafficData.objects.aggregate(
        avg=Avg('vehicle_count')
    )['avg'] or 0

    context = {
        'total_records': total_records,
        'low_count': stats_dict.get('Low', 0),
        'medium_count': stats_dict.get('Medium', 0),
        'high_count': stats_dict.get('High', 0),
        'hotspots': list(hotspots),
        'avg_vehicles': round(avg_vehicles, 1),
        'page_title': 'Dashboard - Traffic Prediction System',
    }

    return render(request, 'home.html', context)


# ============================================================================
# PREDICTION VIEW
# ============================================================================

def predict(request):
    """
    Render the prediction tool page.

    Displays a form where users can input traffic parameters
    and get real-time congestion predictions.

    Args:
        request: HttpRequest object

    Returns:
        HttpResponse: Rendered predict.html template
    """
    context = {
        'page_title': 'Congestion Predictor - Traffic Prediction System',
        'locations': TrafficData.LOCATION_CHOICES,
        'weather_options': TrafficData.WEATHER_CHOICES,
    }
    return render(request, 'predict.html', context)


@csrf_exempt
def predict_api(request):
    """
    API endpoint for traffic congestion prediction.

    Accepts POST request with traffic parameters and returns
    the ML model's prediction.

    Expected POST data:
        - date: Date string (YYYY-MM-DD)
        - time: Time string (HH:MM)
        - location: Location name
        - vehicle_count: Integer number of vehicles
        - weather: Weather condition

    Returns:
        JsonResponse: Prediction result with congestion level and confidence

    Example response:
        {
            "success": true,
            "prediction": "High",
            "confidence": 0.85,
            "message": "Prediction completed successfully"
        }
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Only POST method is allowed'
        }, status=405)

    try:
        # Parse request data
        data = json.loads(request.body)

        # Extract features
        date_str = data.get('date', '')
        time_str = data.get('time', '')
        location = data.get('location', '')
        vehicle_count = int(data.get('vehicle_count', 0))
        weather = data.get('weather', '')

        # Validate input
        if not all([date_str, time_str, location, weather]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)

        # Parse datetime and extract features
        date_time = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        hour = date_time.hour
        day_of_week = date_time.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        is_rush_hour = 1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0

        # Load model and encoders
        model, encoders, scaler, feature_columns = get_model()

        if model is None:
            # Fallback rule-based prediction if model not available
            prediction = rule_based_prediction(vehicle_count, weather, hour, is_rush_hour)

            # Save prediction to database
            saved, record_id, save_message = save_prediction_to_database(
                date_time=date_time,
                location=location,
                vehicle_count=vehicle_count,
                weather=weather,
                congestion_level=prediction
            )

            return JsonResponse({
                'success': True,
                'prediction': prediction,
                'confidence': 0.75,
                'method': 'rule_based',
                'message': 'Using rule-based prediction (ML model not trained yet)',
                'saved': saved,
                'record_id': record_id,
                'save_message': save_message
            })

        # Encode categorical features
        try:
            location_encoded = encoders['location'].transform([location])[0]
            weather_encoded = encoders['weather'].transform([weather])[0]
        except ValueError:
            # Handle unseen categories
            return JsonResponse({
                'success': False,
                'error': f'Invalid location or weather value. Location: {location}, Weather: {weather}'
            }, status=400)

        # Prepare feature vector
        features = np.array([[vehicle_count, location_encoded, weather_encoded, hour, day_of_week, is_rush_hour]])

        # Scale numerical features (if scaler exists)
        if scaler is not None:
            features[:, [0, 3]] = scaler.transform(features[:, [0, 3]])

        # Make prediction
        prediction_encoded = model.predict(features)[0]
        prediction = encoders['congestion'].inverse_transform([prediction_encoded])[0]

        # Get prediction probabilities (confidence)
        probabilities = model.predict_proba(features)[0]
        confidence = float(max(probabilities))

        # Save prediction to database
        saved, record_id, save_message = save_prediction_to_database(
            date_time=date_time,
            location=location,
            vehicle_count=vehicle_count,
            weather=weather,
            congestion_level=prediction
        )

        return JsonResponse({
            'success': True,
            'prediction': prediction,
            'confidence': round(confidence, 3),
            'probabilities': {
                'Low': round(probabilities[0], 3),
                'Medium': round(probabilities[1], 3),
                'High': round(probabilities[2], 3),
            },
            'method': 'ml_model',
            'message': f'Prediction: {prediction} congestion',
            'saved': saved,
            'record_id': record_id,
            'save_message': save_message
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def rule_based_prediction(vehicle_count, weather, hour, is_rush_hour):
    """
    Fallback rule-based prediction when ML model is unavailable.

    Rules:
        - High vehicle count (> 150) during rush hour = High
        - Rainy weather with high vehicle count = High
        - Low vehicle count (< 50) = Low
        - Otherwise = Medium

    Args:
        vehicle_count: Number of vehicles
        weather: Weather condition
        hour: Hour of day (0-23)
        is_rush_hour: Boolean indicating rush hour

    Returns:
        str: Predicted congestion level (Low/Medium/High)
    """
    if vehicle_count > 150 or (vehicle_count > 100 and is_rush_hour):
        return 'High'
    elif vehicle_count < 50:
        return 'Low'
    elif weather == 'Rainy' and vehicle_count > 80:
        return 'High'
    else:
        return 'Medium'


def save_prediction_to_database(date_time, location, vehicle_count, weather, congestion_level):
    """
    Save prediction result to TrafficData database table.

    Args:
        date_time: DateTime object of the prediction
        location: Location string (must match LOCATION_CHOICES)
        vehicle_count: Integer number of vehicles
        weather: Weather condition (must match WEATHER_CHOICES)
        congestion_level: Predicted congestion level (Low/Medium/High)

    Returns:
        tuple: (success: bool, record_id: int/None, message: str)
    """
    try:
        with transaction.atomic():
            # Check for duplicate records (skip if exists)
            existing = TrafficData.objects.filter(
                date_time=date_time,
                location=location,
                vehicle_count=vehicle_count
            ).first()

            if existing:
                return False, None, f"Duplicate prediction already exists (ID: {existing.id})"

            # Create new record
            record = TrafficData.objects.create(
                date_time=date_time,
                location=location,
                vehicle_count=vehicle_count,
                weather=weather,
                congestion_level=congestion_level
            )

            return True, record.id, "Prediction saved to database successfully"

    except Exception as e:
        return False, None, f"Error saving to database: {str(e)}"


# ============================================================================
# ANALYSIS VIEW
# ============================================================================

def analysis(request):
    """
    Render the analysis page with interactive charts.

    Displays:
        - Traffic volume by hour (Bar chart)
        - Congestion level distribution (Pie chart)
        - Location-wise statistics
        - Weather impact analysis

    Args:
        request: HttpRequest object

    Returns:
        HttpResponse: Rendered analysis.html template
    """
    context = {
        'page_title': 'Traffic Analysis - Traffic Prediction System',
    }
    return render(request, 'analysis.html', context)


def analysis_api(request):
    """
    API endpoint for analysis chart data.

    Returns aggregated data for:
        - Hourly traffic distribution
        - Congestion level counts
        - Location-wise statistics
        - Weather-based statistics

    Returns:
        JsonResponse: Aggregated statistics for chart visualization

    Example response:
        {
            "hourly_data": [10, 25, 45, ...],
            "congestion_distribution": {"Low": 100, "Medium": 200, "High": 150},
            ...
        }
    """
    try:
        # Get hourly traffic distribution
        hourly_data = []
        for hour in range(24):
            count = TrafficData.objects.filter(
                date_time__hour=hour
            ).count()
            hourly_data.append(count)

        # Get congestion level distribution
        congestion_dist = TrafficData.objects.values('congestion_level').annotate(
            count=Count('id')
        )
        congestion_data = {item['congestion_level']: item['count'] for item in congestion_dist}

        # Ensure all levels are present
        for level in ['Low', 'Medium', 'High']:
            if level not in congestion_data:
                congestion_data[level] = 0

        # Get location-wise statistics
        location_stats = TrafficData.objects.values('location').annotate(
            total_count=Count('id'),
            avg_vehicles=Avg('vehicle_count')
        ).order_by('-total_count')[:10]

        # Get weather-based statistics
        weather_stats = TrafficData.objects.values('weather').annotate(
            count=Count('id'),
            avg_congestion_high=Count('id', filter=Q(congestion_level='High'))
        )

        # Get day of week distribution
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_data = []
        for day in range(7):
            count = TrafficData.objects.filter(
                date_time__week_day=day + 1  # Django uses 1-7 for Monday-Sunday
            ).count()
            day_data.append(count)

        return JsonResponse({
            'success': True,
            'data': {
                'hourly': hourly_data,
                'congestion': congestion_data,
                'locations': list(location_stats),
                'weather': list(weather_stats),
                'days': day_data,
                'day_names': day_names,
            },
            'total_records': TrafficData.objects.count()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# UTILITY VIEWS
# ============================================================================

def get_locations(request):
    """
    API endpoint to get available locations.

    Returns a list of all traffic locations in the system.

    Args:
        request: HttpRequest object

    Returns:
        JsonResponse: List of locations
    """
    locations = [choice[0] for choice in TrafficData.LOCATION_CHOICES]
    return JsonResponse({'locations': locations})
