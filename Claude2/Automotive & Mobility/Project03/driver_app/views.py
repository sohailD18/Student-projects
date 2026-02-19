from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Count
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import DriverData
from .ai_utils import analyze_driver_behavior


# ==================== Authentication Views ====================

def user_login(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('driver_app:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            next_page = request.GET.get('next', '')
            if next_page:
                return redirect(next_page)
            return redirect('driver_app:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def user_register(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('driver_app:home')

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
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        messages.success(request, f'Account created successfully! Welcome, {username}!')
        return redirect('driver_app:home')

    return render(request, 'register.html')


def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('driver_app:login')


def user_profile(request):
    """
    User profile view.
    """
    if not request.user.is_authenticated:
        return redirect('driver_app:login')

    # Get user's trip data (if driver_name matches username)
    user_trips = DriverData.objects.filter(driver_name__iexact=request.user.username)
    analyzed_trips = user_trips.filter(risk_score__isnull=False)

    # Calculate statistics
    total_trips = user_trips.count()
    avg_risk_score = 0
    avg_speed = 0
    safe_trips_count = 0

    if analyzed_trips.exists():
        avg_risk_score = round(analyzed_trips.aggregate(Avg('risk_score'))['risk_score__avg'] or 0, 2)

    if user_trips.exists():
        avg_speed = round(user_trips.aggregate(Avg('average_speed'))['average_speed__avg'] or 0, 1)
        safe_trips_count = analyzed_trips.filter(behavior_class='Safe').count()

    context = {
        'user': request.user,
        'user_trips': user_trips,
        'total_trips': total_trips,
        'avg_risk_score': avg_risk_score,
        'avg_speed': avg_speed,
        'safe_trips_count': safe_trips_count,
    }

    return render(request, 'profile.html', context)


@login_required
def home(request):
    """
    Dashboard view displaying driver behavior analysis.
    Shows recent trips, statistics, and charts.
    """
    # Get all driver data
    all_records = DriverData.objects.all()

    # Calculate statistics
    total_trips = all_records.count()
    analyzed_trips = all_records.filter(risk_score__isnull=False)

    # Get recent trips (last 10)
    recent_trips = all_records[:10]

    # Calculate averages
    stats = {
        'total_trips': total_trips,
        'analyzed_trips': analyzed_trips.count(),
        'avg_risk_score': 0,
        'avg_safety': 0,
        'safe_drivers': 0,
        'moderate_drivers': 0,
        'risky_drivers': 0,
    }

    if analyzed_trips.exists():
        stats['avg_risk_score'] = round(analyzed_trips.aggregate(Avg('risk_score'))['risk_score__avg'] or 0, 2)
        stats['avg_safety'] = round(100 - stats['avg_risk_score'], 2)
        stats['safe_drivers'] = analyzed_trips.filter(behavior_class='Safe').count()
        stats['moderate_drivers'] = analyzed_trips.filter(behavior_class='Moderate').count()
        stats['risky_drivers'] = analyzed_trips.filter(behavior_class='Risky').count()

    # Prepare chart data for the last 30 days
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_data = all_records.filter(trip_date__gte=thirty_days_ago).order_by('trip_date')

    chart_labels = []
    chart_risk_scores = []
    chart_speeds = []

    for record in recent_data:
        chart_labels.append(record.trip_date.strftime('%Y-%m-%d'))
        chart_risk_scores.append(record.risk_score or 0)
        chart_speeds.append(record.average_speed)

    context = {
        'recent_trips': recent_trips,
        'stats': stats,
        'chart_labels': chart_labels,
        'chart_risk_scores': chart_risk_scores,
        'chart_speeds': chart_speeds,
    }

    return render(request, 'dashboard.html', context)


@login_required
def add_data(request):
    """
    Form view to submit new driving data.
    Handles both GET (display form) and POST (process form).
    """
    if request.method == 'POST':
        try:
            # Extract form data
            driver_name = request.POST.get('driver_name')
            trip_date = request.POST.get('trip_date')
            average_speed = float(request.POST.get('average_speed', 0))
            max_speed = float(request.POST.get('max_speed', 0))
            harsh_braking_events = int(request.POST.get('harsh_braking_events', 0))
            rapid_acceleration_events = int(request.POST.get('rapid_acceleration_events', 0))
            cornering_speed = float(request.POST.get('cornering_speed', 0))

            # Validate data
            if not driver_name or not trip_date:
                messages.error(request, 'Please provide all required fields.')
                return render(request, 'add_trip.html')

            if average_speed < 0 or max_speed < 0 or harsh_braking_events < 0 or rapid_acceleration_events < 0:
                messages.error(request, 'Values cannot be negative.')
                return render(request, 'add_trip.html')

            # Create DriverData instance
            driver_data = DriverData.objects.create(
                driver_name=driver_name,
                trip_date=datetime.strptime(trip_date, '%Y-%m-%d').date(),
                average_speed=average_speed,
                max_speed=max_speed,
                harsh_braking_events=harsh_braking_events,
                rapid_acceleration_events=rapid_acceleration_events,
                cornering_speed=cornering_speed,
            )

            # Analyze the data using AI
            analysis_result = analyze_driver_behavior({
                'average_speed': average_speed,
                'max_speed': max_speed,
                'harsh_braking_events': harsh_braking_events,
                'rapid_acceleration_events': rapid_acceleration_events,
                'cornering_speed': cornering_speed,
            })

            # Update the record with AI results
            driver_data.risk_score = analysis_result['risk_score']
            driver_data.behavior_class = analysis_result['behavior_class']
            driver_data.recommendations = analysis_result['recommendations']
            driver_data.save()

            messages.success(
                request,
                f'Data analyzed successfully! '
                f'Risk Score: {analysis_result["risk_score"]} - '
                f'Classification: {analysis_result["behavior_class"]}'
            )

            return redirect('home')

        except ValueError as e:
            messages.error(request, f'Invalid data format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error processing data: {str(e)}')

    return render(request, 'add_trip.html')


def analyze(request):
    """
    API endpoint to analyze existing data or process new data.
    Returns JSON response with analysis results.
    """
    if request.method == 'POST':
        try:
            # Get data from request
            data = request.POST if request.content_type == 'multipart/form-data' else request.JSON

            # Prepare driving data for analysis
            driving_data = {
                'average_speed': float(data.get('average_speed', 0)),
                'max_speed': float(data.get('max_speed', 0)),
                'harsh_braking_events': int(data.get('harsh_braking_events', 0)),
                'rapid_acceleration_events': int(data.get('rapid_acceleration_events', 0)),
                'cornering_speed': float(data.get('cornering_speed', 0)),
            }

            # Analyze using AI
            result = analyze_driver_behavior(driving_data)

            # If save_data is True, save to database
            if data.get('save_data', False):
                DriverData.objects.create(
                    driver_name=data.get('driver_name', 'Unknown'),
                    trip_date=datetime.strptime(data.get('trip_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
                    average_speed=driving_data['average_speed'],
                    max_speed=driving_data['max_speed'],
                    harsh_braking_events=driving_data['harsh_braking_events'],
                    rapid_acceleration_events=driving_data['rapid_acceleration_events'],
                    cornering_speed=driving_data['cornering_speed'],
                    risk_score=result['risk_score'],
                    behavior_class=result['behavior_class'],
                    recommendations=result['recommendations'],
                )

            return JsonResponse({
                'success': True,
                'analysis': result,
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=400)

    # GET request - return analysis form
    return render(request, 'analyze.html')


def trip_detail(request, trip_id):
    """
    Display detailed information about a specific trip.
    """
    try:
        trip = DriverData.objects.get(id=trip_id)
        context = {
            'trip': trip,
        }
        return render(request, 'trip_detail.html', context)
    except DriverData.DoesNotExist:
        messages.error(request, 'Trip not found.')
        return redirect('home')


def driver_report(request, driver_name):
    """
    Generate a comprehensive report for a specific driver.
    Shows all trips and overall statistics.
    """
    trips = DriverData.objects.filter(driver_name__iexact=driver_name)

    if not trips.exists():
        messages.error(request, f'No data found for driver: {driver_name}')
        return redirect('home')

    # Calculate driver statistics
    analyzed_trips = trips.filter(risk_score__isnull=False)

    stats = {
        'driver_name': driver_name,
        'total_trips': trips.count(),
        'avg_risk_score': 0,
        'avg_speed': 0,
        'total_braking_events': 0,
        'total_acceleration_events': 0,
        'behavior_distribution': {
            'Safe': 0,
            'Moderate': 0,
            'Risky': 0,
        },
    }

    if analyzed_trips.exists():
        stats['avg_risk_score'] = round(analyzed_trips.aggregate(Avg('risk_score'))['risk_score__avg'] or 0, 2)
        stats['avg_speed'] = round(trips.aggregate(Avg('average_speed'))['average_speed__avg'] or 0, 2)
        stats['total_braking_events'] = trips.aggregate(total=Count('harsh_braking_events'))['total'] or 0
        stats['total_acceleration_events'] = trips.aggregate(total=Count('rapid_acceleration_events'))['total'] or 0

        for behavior_class in ['Safe', 'Moderate', 'Risky']:
            stats['behavior_distribution'][behavior_class] = analyzed_trips.filter(
                behavior_class=behavior_class
            ).count()

    context = {
        'trips': trips,
        'stats': stats,
    }

    return render(request, 'driver_report.html', context)


def api_chart_data(request):
    """
    API endpoint to provide chart data for dashboard visualizations.
    Returns JSON with historical data for charts.
    """
    # Get data from last 30 days
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_data = DriverData.objects.filter(
        trip_date__gte=thirty_days_ago,
        risk_score__isnull=False
    ).order_by('trip_date')

    # Prepare data
    dates = []
    risk_scores = []
    safety_scores = []

    for record in recent_data:
        dates.append(record.trip_date.strftime('%Y-%m-%d'))
        risk_scores.append(record.risk_score)
        safety_scores.append(100 - record.risk_score)

    return JsonResponse({
        'dates': dates,
        'risk_scores': risk_scores,
        'safety_scores': safety_scores,
    })
