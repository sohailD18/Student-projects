"""
Django views for Route Planner Application
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
import json
from datetime import datetime
from .optimization_engine import RouteOptimizer, AnalyticsEngine
from .models import Location, Route, RouteHistory, OptimizationMetrics


# Initialize optimization engines
route_optimizer = RouteOptimizer()
analytics_engine = AnalyticsEngine()


def index(request):
    """
    Main route planner page
    """
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def calculate_routes(request):
    """
    API endpoint to calculate routes between two locations
    Expects JSON: {origin_name, origin_lat, origin_lng, destination_name, destination_lat, destination_lng}
    """
    try:
        data = json.loads(request.body)

        # Extract input data
        origin_name = data.get('origin_name', 'Origin')
        origin_lat = float(data.get('origin_lat', 0))
        origin_lng = float(data.get('origin_lng', 0))
        destination_name = data.get('destination_name', 'Destination')
        destination_lat = float(data.get('destination_lat', 0))
        destination_lng = float(data.get('destination_lng', 0))

        # Validate coordinates
        if not all([origin_lat, origin_lng, destination_lat, destination_lng]):
            return JsonResponse({
                'error': 'Invalid coordinates',
                'message': 'All latitude and longitude values are required'
            }, status=400)

        # Generate route options
        routes = route_optimizer.generate_route_variations(
            origin_lat, origin_lng, destination_lat, destination_lng
        )

        # Save to database (create or get locations)
        origin_location, _ = Location.objects.get_or_create(
            name=origin_name,
            defaults={
                'latitude': origin_lat,
                'longitude': origin_lng,
                'city': 'Unknown',
                'country': 'USA'
            }
        )

        dest_location, _ = Location.objects.get_or_create(
            name=destination_name,
            defaults={
                'latitude': destination_lat,
                'longitude': destination_lng,
                'city': 'Unknown',
                'country': 'USA'
            }
        )

        # Save routes to database
        for route_type, route_data in routes.items():
            if route_type == 'metadata':
                continue

            Route.objects.create(
                origin=origin_location,
                destination=dest_location,
                route_type=route_type,
                distance_km=route_data['distance_km'],
                estimated_time_minutes=route_data['estimated_time_minutes'],
                path_coordinates=route_data['coordinates'],
                traffic_factor=route_data['traffic_factor'],
                fuel_cost_estimate=route_data['fuel_cost'],
                co2_emission_kg=route_data['co2_emission_kg'],
                is_recommended=route_data.get('is_recommended', False)
            )

        # Save to history
        recommended_route = next((r for r in routes.values() if r.get('is_recommended')), routes.get('fastest', {}))

        RouteHistory.objects.create(
            user=request.user if request.user.is_authenticated else None,
            origin_name=origin_name,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            destination_name=destination_name,
            destination_lat=destination_lat,
            destination_lng=destination_lng,
            selected_route_type=recommended_route.get('type', 'fastest'),
            distance_km=recommended_route.get('distance_km', 0),
            estimated_time_minutes=recommended_route.get('estimated_time_minutes', 0),
            fuel_cost=recommended_route.get('fuel_cost', 0.0),
            available_routes=routes,
            optimization_score=routes.get('metadata', {}).get('optimization_score', 0)
        )

        return JsonResponse({
            'success': True,
            'origin': {'name': origin_name, 'lat': origin_lat, 'lng': origin_lng},
            'destination': {'name': destination_name, 'lat': destination_lat, 'lng': destination_lng},
            'routes': routes,
            'calculated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'error': 'Calculation failed',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_analytics(request):
    """
    API endpoint to get analytics data for charts
    """
    try:
        # Generate analytics data
        hourly_traffic = analytics_engine.generate_hourly_traffic_pattern()
        weekly_comparison = analytics_engine.generate_weekly_comparison()
        route_distribution = analytics_engine.generate_route_type_distribution()
        efficiency_trend = analytics_engine.generate_efficiency_trend(days=30)

        return JsonResponse({
            'success': True,
            'data': {
                'hourly_traffic': hourly_traffic,
                'weekly_comparison': weekly_comparison,
                'route_distribution': route_distribution,
                'efficiency_trend': efficiency_trend
            }
        })

    except Exception as e:
        return JsonResponse({
            'error': 'Analytics generation failed',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_route_history(request):
    """
    API endpoint to get route calculation history
    """
    try:
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        # Get queryset
        queryset = RouteHistory.objects.all().order_by('-created_at')

        # Paginate
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        # Serialize data
        history_data = []
        for item in page_obj:
            history_data.append({
                'id': item.id,
                'origin_name': item.origin_name,
                'destination_name': item.destination_name,
                'route_type': item.selected_route_type,
                'distance_km': item.distance_km,
                'estimated_time': item.estimated_time_minutes,
                'fuel_cost': item.fuel_cost,
                'optimization_score': item.optimization_score,
                'created_at': item.created_at.isoformat()
            })

        return JsonResponse({
            'success': True,
            'data': history_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count
            }
        })

    except Exception as e:
        return JsonResponse({
            'error': 'Failed to fetch history',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def export_report(request):
    """
    API endpoint to generate and export route report
    Expects JSON: {route_data, origin, destination, selected_route}
    """
    try:
        data = json.loads(request.body)
        route_data = data.get('route_data', {})
        origin = data.get('origin', {})
        destination = data.get('destination', {})
        selected_route = data.get('selected_route', 'fastest')

        # Generate report content
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("INTELLIGENT ROUTE PLANNING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"\nORIGIN: {origin.get('name', 'Unknown')}")
        report_lines.append(f"Coordinates: {origin.get('lat', 0):.6f}, {origin.get('lng', 0):.6f}")
        report_lines.append(f"\nDESTINATION: {destination.get('name', 'Unknown')}")
        report_lines.append(f"Coordinates: {destination.get('lat', 0):.6f}, {destination.get('lng', 0):.6f}")

        report_lines.append("\n" + "-" * 80)
        report_lines.append("AVAILABLE ROUTES")
        report_lines.append("-" * 80)

        # Display all routes
        for route_type, route_info in route_data.items():
            if route_type == 'metadata':
                continue

            is_recommended = " ★ RECOMMENDED" if route_info.get('is_recommended') else ""
            report_lines.append(f"\n{route_info.get('name', route_type).upper()}{is_recommended}")
            report_lines.append(f"  Distance: {route_info.get('distance_km', 0):.2f} km")
            report_lines.append(f"  Estimated Time: {route_info.get('estimated_time_minutes', 0)} minutes")
            report_lines.append(f"  Traffic Factor: {route_info.get('traffic_factor', 1.0):.2f}")
            report_lines.append(f"  Fuel Cost: ${route_info.get('fuel_cost', 0):.2f}")
            report_lines.append(f"  CO2 Emissions: {route_info.get('co2_emission_kg', 0):.2f} kg")
            report_lines.append(f"  Description: {route_info.get('description', 'N/A')}")

        # Add optimization score
        metadata = route_data.get('metadata', {})
        report_lines.append("\n" + "-" * 80)
        report_lines.append(f"OPTIMIZATION SCORE: {metadata.get('optimization_score', 0):.1f}/100")
        report_lines.append("-" * 80)

        # Add footer
        report_lines.append("\n" + "=" * 80)
        report_lines.append("Generated by AI-Powered Route Optimization Engine")
        report_lines.append("=" * 80)

        report_text = "\n".join(report_lines)

        return JsonResponse({
            'success': True,
            'report': report_text,
            'filename': f"route_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        })

    except Exception as e:
        return JsonResponse({
            'error': 'Report generation failed',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_dashboard_stats(request):
    """
    API endpoint to get dashboard statistics
    """
    try:
        total_routes = RouteHistory.objects.count()
        avg_optimization_score = RouteHistory.objects.aggregate(
            avg_score=models.Avg('optimization_score')
        )['avg_score'] or 0

        total_distance = RouteHistory.objects.aggregate(
            total_dist=models.Sum('distance_km')
        )['total_dist'] or 0

        total_fuel_saved = total_routes * 2.5  # Simulated

        return JsonResponse({
            'success': True,
            'stats': {
                'total_routes_calculated': total_routes,
                'avg_optimization_score': round(avg_optimization_score, 1),
                'total_distance_km': round(total_distance, 2),
                'total_fuel_saved_liters': round(total_fuel_saved, 2),
                'co2_emissions_saved_kg': round(total_fuel_saved * 2.31, 2)
            }
        })

    except Exception as e:
        return JsonResponse({
            'error': 'Failed to fetch stats',
            'message': str(e)
        }, status=500)


# Authentication Views

def login_page(request):
    """
    Login page
    """
    # If already logged in, redirect to index
    if request.user.is_authenticated:
        return redirect('route_planner:index')

    return render(request, 'login.html')


def register_page(request):
    """
    Registration page
    """
    # If already logged in, redirect to index
    if request.user.is_authenticated:
        return redirect('route_planner:index')

    return render(request, 'register.html')


@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    """
    Handle user login via AJAX
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password are required'
            }, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'username': user.username,
                'email': user.email
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password'
            }, status=401)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    """
    Handle user registration via AJAX
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        # Validate required fields
        if not all([username, email, password]):
            return JsonResponse({
                'success': False,
                'error': 'Username, email, and password are required'
            }, status=400)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'error': 'Username already exists'
            }, status=400)

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'Email already exists'
            }, status=400)

        # Validate password length
        if len(password) < 6:
            return JsonResponse({
                'success': False,
                'error': 'Password must be at least 6 characters long'
            }, status=400)

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Auto-login after registration
        login(request, user)

        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'username': user.username,
            'email': user.email
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def logout_user(request):
    """
    Handle user logout
    """
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Logged out successfully'
    })


@login_required
def profile_page(request):
    """
    User profile page showing their route history
    """
    # Get user's route history
    user_history = RouteHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]

    context = {
        'user_history': user_history,
        'total_routes': user_history.count(),
        'total_distance': sum(h.distance_km for h in user_history),
        'total_cost_saved': user_history.count() * 2.5  # Simulated
    }

    return render(request, 'profile.html', context)
