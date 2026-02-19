"""
Views for AI Trip Planner System.
Handles route calculation, AI prediction, and rendering templates.
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.cache import cache
from core.models import Location, TripHistory, UserPreference, RouteSuggestion
import os
import joblib
import numpy as np
from django.conf import settings
from math import radians, cos, sin, asin, sqrt
import random
import uuid
import json
from django.utils import timezone
from datetime import timedelta


# ============= AI MODEL LOADING =============

def load_ai_model():
    """
    Load the trained AI model and feature names.
    Returns None if model files don't exist.
    """
    model_path = os.path.join(settings.BASE_DIR, 'travel_model.pkl')
    features_path = os.path.join(settings.BASE_DIR, 'model_features.pkl')

    if os.path.exists(model_path) and os.path.exists(features_path):
        try:
            model = joblib.load(model_path)
            feature_names = joblib.load(features_path)
            return model, feature_names
        except Exception as e:
            print(f"Error loading model: {e}")
            return None, None
    return None, None


def predict_travel_time(distance_km, traffic_level, weather, transport_mode='car'):
    """
    Use the AI model to predict travel time.
    Falls back to calculation if model is unavailable.

    Args:
        distance_km: Distance in kilometers
        traffic_level: Traffic level (1-10)
        weather: Weather condition string
        transport_mode: Mode of transport

    Returns:
        Predicted travel time in minutes
    """
    model, feature_names = load_ai_model()

    if model is None:
        # Fallback to basic calculation
        return calculate_travel_time_fallback(distance_km, traffic_level, weather, transport_mode)

    # Encode the features
    weather_mapping = {'clear': 0, 'cloudy': 1, 'rain': 2, 'heavy_rain': 3, 'fog': 4}
    transport_mapping = {'car': 0, 'bike': 1, 'bus': 2}

    try:
        weather_encoded = weather_mapping.get(weather, 0)
        transport_encoded = transport_mapping.get(transport_mode, 0)

        # Prepare features in correct order
        features = np.array([[
            distance_km,
            traffic_level,
            weather_encoded,
            transport_encoded
        ]])

        # Predict
        predicted_time = model.predict(features)[0]
        return max(1, round(predicted_time, 2))  # Ensure minimum 1 minute
    except Exception as e:
        print(f"Prediction error: {e}")
        return calculate_travel_time_fallback(distance_km, traffic_level, weather, transport_mode)


def calculate_travel_time_fallback(distance_km, traffic_level, weather, transport_mode='car'):
    """
    Fallback calculation when AI model is unavailable.
    Uses basic speed estimates with traffic and weather factors.
    """
    # Base speeds in km/h
    base_speeds = {
        'car': 50,
        'bike': 45,
        'bus': 40,
        'walking': 5,
    }

    base_speed = base_speeds.get(transport_mode, 50)

    # Traffic factor (1.0 = no impact, decreases as traffic increases)
    traffic_factor = 1 - ((traffic_level - 1) * 0.08)
    traffic_factor = max(0.25, traffic_factor)  # Minimum 25% speed

    # Weather penalty
    weather_penalty = {
        'clear': 1.0,
        'cloudy': 1.0,
        'rain': 1.15,
        'heavy_rain': 1.35,
        'fog': 1.25,
        'snow': 1.4,
        'storm': 1.5,
    }
    weather_factor = weather_penalty.get(weather, 1.0)

    # Calculate effective speed
    effective_speed = (base_speed * traffic_factor) / weather_factor

    # Calculate time in minutes
    time_hours = distance_km / effective_speed
    time_minutes = time_hours * 60

    return max(1, round(time_minutes, 2))


# ============= DISTANCE CALCULATION =============

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return round(c * r, 2)


def calculate_fuel_cost(distance_km, transport_mode='car'):
    """
    Calculate estimated fuel cost.

    Args:
        distance_km: Distance in kilometers
        transport_mode: Mode of transport

    Returns:
        Estimated cost in INR
    """
    # Fuel efficiency (km/liter) and fuel price
    fuel_efficiency = {
        'car': 8,
        'bike': 45,
        'bus': 5,
        'walking': 0,
    }

    fuel_price_per_liter = 100  # INR

    if transport_mode == 'walking':
        return 0

    efficiency = fuel_efficiency.get(transport_mode, 8)
    liters_needed = distance_km / efficiency
    cost = liters_needed * fuel_price_per_liter

    return round(cost, 2)


# ============= ROUTE GENERATION =============

def generate_route_coordinates(source_lat, source_lon, dest_lat, dest_lon, num_points=20):
    """
    Generate intermediate coordinates between source and destination
    for drawing route polyline on map.

    Args:
        source_lat, source_lon: Source coordinates
        dest_lat, dest_lon: Destination coordinates
        num_points: Number of points to generate

    Returns:
        List of [latitude, longitude] pairs
    """
    coordinates = []

    # Add source
    coordinates.append([source_lat, source_lon])

    # Generate intermediate points (curved path simulation)
    for i in range(1, num_points - 1):
        ratio = i / num_points

        # Linear interpolation
        lat = source_lat + (dest_lat - source_lat) * ratio
        lon = source_lon + (dest_lon - source_lon) * ratio

        # Add slight curve for realism
        curve_factor = 0.02
        lat += random.uniform(-curve_factor, curve_factor) * ratio
        lon += random.uniform(-curve_factor, curve_factor) * ratio

        coordinates.append([round(lat, 6), round(lon, 6)])

    # Add destination
    coordinates.append([dest_lat, dest_lon])

    return coordinates


def generate_routes(source_location, dest_location, traffic_level, weather, transport_mode):
    """
    Generate multiple route options using AI predictions.

    Returns list of route dictionaries with different characteristics.
    """
    distance = haversine_distance(
        source_location.latitude, source_location.longitude,
        dest_location.latitude, dest_location.longitude
    )

    routes = []

    # 1. FASTEST ROUTE - Optimized for time using AI prediction
    predicted_time = predict_travel_time(distance, traffic_level, weather, transport_mode)
    routes.append({
        'name': 'Fastest Route',
        'type': 'fastest',
        'distance': distance,
        'time': predicted_time,
        'fuel_cost': calculate_fuel_cost(distance, transport_mode),
        'description': f'Best time based on current traffic ({traffic_level}/10)',
        'icon': 'lightning',
        'badge_class': 'bg-primary',
        'coordinates': generate_route_coordinates(
            float(source_location.latitude), float(source_location.longitude),
            float(dest_location.latitude), float(dest_location.longitude)
        )
    })

    # 2. SHORTEST ROUTE - Direct distance, slightly longer time
    shortest_distance = distance * 1.05  # 5% longer for more direct roads
    shortest_time = predict_travel_time(shortest_distance, traffic_level, weather, transport_mode)
    routes.append({
        'name': 'Shortest Route',
        'type': 'shortest',
        'distance': round(shortest_distance, 2),
        'time': round(shortest_time, 2),
        'fuel_cost': calculate_fuel_cost(shortest_distance, transport_mode),
        'description': 'Minimum distance via major highways',
        'icon': 'signpost',
        'badge_class': 'bg-success',
        'coordinates': generate_route_coordinates(
            float(source_location.latitude), float(source_location.longitude),
            float(dest_location.latitude), float(dest_location.longitude),
            num_points=15
        )
    })

    # 3. SCENIC/ECO ROUTE - Longer distance, better experience
    scenic_distance = distance * 1.25  # 25% longer
    scenic_time = predict_travel_time(scenic_distance, max(1, traffic_level - 2), weather, transport_mode)
    routes.append({
        'name': 'Scenic Route',
        'type': 'scenic',
        'distance': round(scenic_distance, 2),
        'time': round(scenic_time, 2),
        'fuel_cost': calculate_fuel_cost(scenic_distance, transport_mode),
        'description': 'Beautiful views with less traffic',
        'icon': 'tree',
        'badge_class': 'bg-info',
        'coordinates': generate_route_coordinates(
            float(source_location.latitude), float(source_location.longitude),
            float(dest_location.latitude), float(dest_location.longitude),
            num_points=30
        )
    })

    # Sort by time (fastest first)
    routes.sort(key=lambda x: x['time'])

    return routes


# ============= VIEW FUNCTIONS =============

def home(request):
    """
    Home page with trip planning form.
    """
    # Get all locations for dropdown
    locations = Location.objects.all().order_by('is_popular', 'name')

    # Get user's session ID for preferences
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    # Get or create user preferences
    try:
        preferences = UserPreference.objects.get(session_id=session_id)
    except UserPreference.DoesNotExist:
        preferences = UserPreference.objects.create(
            session_id=session_id,
            preferred_transport_mode='car',
            route_priority='time'
        )

    context = {
        'locations': locations,
        'preferences': preferences,
        'weather_options': ['clear', 'cloudy', 'rain', 'heavy_rain', 'fog'],
        'transport_modes': [
            ('car', 'Car'),
            ('bike', 'Motorcycle'),
            ('bus', 'Bus'),
        ],
    }

    return render(request, 'index.html', context)


def plan_trip(request):
    """
    Handle trip planning form submission and generate routes.
    """
    if request.method != 'POST':
        return redirect('home')

    # Get form data
    source_id = request.POST.get('source_location')
    dest_id = request.POST.get('destination_location')
    traffic_level = int(request.POST.get('traffic_level', 4))
    weather = request.POST.get('weather', 'clear')
    transport_mode = request.POST.get('transport_mode', 'car')

    # Validate inputs
    if not source_id or not dest_id:
        messages.error(request, 'Please select both source and destination locations.')
        return redirect('home')

    if source_id == dest_id:
        messages.error(request, 'Source and destination cannot be the same.')
        return redirect('home')

    # Get location objects
    try:
        source_location = Location.objects.get(id=source_id)
        dest_location = Location.objects.get(id=dest_id)
    except Location.DoesNotExist:
        messages.error(request, 'Invalid location selected.')
        return redirect('home')

    # Generate routes
    routes = generate_routes(source_location, dest_location, traffic_level, weather, transport_mode)

    # Save to trip history for learning
    TripHistory.objects.create(
        source=source_location,
        destination=dest_location,
        distance=routes[0]['distance'],  # Save the fastest route distance
        traffic_level=traffic_level,
        travel_time=routes[0]['time'],  # Save the fastest route time
        weather_condition=weather,
        transport_mode=transport_mode,
        route_type=routes[0]['type'],
        fuel_cost=routes[0]['fuel_cost'],
        date_of_travel=timezone.now()
    )

    # Update user preferences
    session_id = request.session.session_key
    if session_id:
        UserPreference.objects.update_or_create(
            session_id=session_id,
            defaults={
                'preferred_transport_mode': transport_mode,
            }
        )

    # Prepare context for template
    # Convert coordinates to lists for JSON serialization
    routes_json = []
    for route in routes:
        route_data = route.copy()
        route_data['coordinates'] = [[float(lat), float(lon)] for lat, lon in route['coordinates']]
        routes_json.append(route_data)

    context = {
        'source': source_location,
        'destination': dest_location,
        'routes': routes,
        'routes_json': json.dumps(routes_json),
        'traffic_level': traffic_level,
        'weather': weather,
        'transport_mode': transport_mode,
    }

    return render(request, 'result.html', context)


def location_search(request):
    """
    API endpoint for location search/autocomplete.
    Returns JSON response with matching locations.
    """
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'locations': []})

    # Search in name, city, state
    locations = Location.objects.filter(
        name__icontains=query
    ) | Location.objects.filter(
        city__icontains=query
    ) | Location.objects.filter(
        state__icontains=query
    )

    locations = locations[:10]  # Limit to 10 results

    results = []
    for loc in locations:
        results.append({
            'id': str(loc.id),
            'name': loc.name,
            'city': loc.city,
            'state': loc.state,
            'full_address': f"{loc.name}, {loc.city}",
            'latitude': float(loc.latitude),
            'longitude': float(loc.longitude),
        })

    return JsonResponse({'locations': results})


def about(request):
    """
    About page with project information.
    """
    return render(request, 'about.html')
