"""
Fleet Management System Views

This module contains all views for:
- Dashboard with KPI visualizations
- Vehicle CRUD operations
- AI Analytics and predictions
- CSV Reporting
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q, Avg, F, Case, When, IntegerField, DecimalField, Value
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json

from .models import Vehicle, Driver, Trip, MaintenanceRecord, Alert
from .utils import (
    FleetAnalytics,
    PredictiveMaintenanceAI,
    AlertGenerator,
    CostOptimizer
)


# ===============================
# Dashboard View
# ===============================

def dashboard(request):
    """
    Main dashboard view with KPIs and visualizations
    """
    # Get KPIs
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(status='active').count()
    total_drivers = Driver.objects.filter(status='active').count()
    total_trips = Trip.objects.filter(status='completed').count()

    # Active alerts
    active_alerts = Alert.objects.filter(is_active=True).count()
    critical_alerts = Alert.objects.filter(is_active=True, severity='critical').count()

    # Fleet availability
    available_vehicles = active_vehicles
    vehicles_in_maintenance = Vehicle.objects.filter(status='maintenance').count()

    # Calculate totals
    total_distance = Trip.objects.aggregate(
        total=Coalesce(Sum('distance'), Value(0, output_field=DecimalField()), output_field=DecimalField())
    )['total'] or 0

    total_fuel_used = Trip.objects.aggregate(
        total=Coalesce(Sum('fuel_used'), Value(0, output_field=DecimalField()), output_field=DecimalField())
    )['total'] or 0

    avg_fuel_efficiency = round(total_distance / total_fuel_used, 2) if total_fuel_used > 0 else 0

    # Total maintenance cost
    total_maintenance_cost = MaintenanceRecord.objects.aggregate(
        total=Coalesce(Sum('cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
    )['total'] or 0

    # Monthly costs for chart
    monthly_costs = FleetAnalytics.get_monthly_costs()

    # Prepare chart data
    if not monthly_costs.empty:
        chart_data = monthly_costs.groupby('year_month')['cost'].sum().reset_index()
        monthly_cost_labels = chart_data['year_month'].tolist()
        monthly_cost_data = chart_data['cost'].tolist()
    else:
        # Generate sample data for demonstration
        monthly_cost_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        monthly_cost_data = [1200, 1900, 1500, 2100, 1800, 2300]

    # Fuel efficiency trends
    efficiency_trends = FleetAnalytics.get_fuel_efficiency_trends()

    if not efficiency_trends.empty:
        efficiency_labels = efficiency_trends['year_month'].unique().tolist()[:6]
        efficiency_data = []
        for vehicle in Vehicle.objects.all()[:5]:  # Top 5 vehicles
            vehicle_data = efficiency_trends[
                efficiency_trends['vehicle__plate'] == vehicle.plate
            ]['fuel_efficiency'].tolist()
            efficiency_data.append({
                'label': vehicle.plate,
                'data': vehicle_data[:6]
            })
    else:
        efficiency_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        efficiency_data = [
            {'label': 'ABC-123', 'data': [25, 26, 24, 27, 25, 26]},
            {'label': 'XYZ-456', 'data': [22, 23, 21, 24, 22, 23]},
        ]

    # Recent alerts
    recent_alerts = Alert.objects.filter(is_active=True).order_by('-created_at')[:10]

    # Predictive maintenance flags
    ai = PredictiveMaintenanceAI()
    predictive_flags = []

    for vehicle in Vehicle.objects.filter(status='active')[:5]:
        prediction = ai.predict_next_maintenance_mileage(vehicle)
        failure_pred = ai.predict_failure_probability(vehicle)

        if prediction['urgency'] in ['critical', 'high'] or failure_pred['risk_level'] in ['critical', 'high']:
            predictive_flags.append({
                'vehicle': vehicle.plate,
                'miles_until': prediction['miles_until_maintenance'],
                'urgency': prediction['urgency'],
                'failure_probability': failure_pred['failure_probability'],
                'risk_level': failure_pred['risk_level']
            })

    # Vehicle status distribution
    status_distribution = {
        'active': Vehicle.objects.filter(status='active').count(),
        'maintenance': Vehicle.objects.filter(status='maintenance').count(),
        'inactive': Vehicle.objects.filter(status='inactive').count(),
        'retired': Vehicle.objects.filter(status='retired').count(),
    }

    context = {
        'page_title': 'Dashboard',
        # KPIs
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'total_drivers': total_drivers,
        'total_trips': total_trips,
        'active_alerts': active_alerts,
        'critical_alerts': critical_alerts,
        'total_distance': round(total_distance, 2),
        'total_fuel_used': round(total_fuel_used, 2),
        'avg_fuel_efficiency': avg_fuel_efficiency,
        'total_maintenance_cost': round(total_maintenance_cost, 2),
        'vehicles_in_maintenance': vehicles_in_maintenance,
        # Chart data
        'monthly_cost_labels': json.dumps(monthly_cost_labels),
        'monthly_cost_data': json.dumps(monthly_cost_data),
        'efficiency_labels': json.dumps(efficiency_labels),
        'efficiency_data': json.dumps(efficiency_data),
        'status_distribution': json.dumps(status_distribution),
        # Alerts and predictions
        'recent_alerts': recent_alerts,
        'predictive_flags': predictive_flags,
    }

    return render(request, 'core/dashboard.html', context)


# ===============================
# Vehicle Views
# ===============================

def vehicle_list(request):
    """
    List all vehicles with status indicators
    """
    vehicles = Vehicle.objects.all()

    # Get efficiency ratings
    efficiency_ratings = CostOptimizer.calculate_efficiency_ratings()
    ratings_dict = {v['vehicle_id']: v for v in efficiency_ratings}

    # Enrich vehicles with ratings
    enriched_vehicles = []
    for vehicle in vehicles:
        vehicle_data = {
            'vehicle': vehicle,
            'total_distance': vehicle.total_distance,
            'fuel_efficiency': vehicle.fuel_efficiency,
            'cost_per_mile': vehicle.cost_per_mile,
            'active_alerts': vehicle.active_alerts_count,
            'rating': ratings_dict.get(vehicle.id, {}).get('rating', 0),
            'rating_label': ratings_dict.get(vehicle.id, {}).get('rating_label', 'N/A')
        }
        enriched_vehicles.append(vehicle_data)

    context = {
        'page_title': 'Fleet Vehicles',
        'vehicles': enriched_vehicles,
    }

    return render(request, 'core/vehicle_list.html', context)


def vehicle_detail(request, vehicle_id):
    """
    Display detailed information about a specific vehicle
    """
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    # Get trips
    trips = Trip.objects.filter(vehicle=vehicle).order_by('-start_date')[:10]

    # Get maintenance records
    maintenance_records = MaintenanceRecord.objects.filter(
        vehicle=vehicle
    ).order_by('-date')[:10]

    # Get active alerts
    alerts = Alert.objects.filter(vehicle=vehicle, is_active=True).order_by('-created_at')

    # Get AI predictions
    ai = PredictiveMaintenanceAI()
    maintenance_prediction = ai.predict_next_maintenance_mileage(vehicle)
    failure_prediction = ai.predict_failure_probability(vehicle)

    context = {
        'page_title': f'Vehicle - {vehicle.plate}',
        'vehicle': vehicle,
        'trips': trips,
        'maintenance_records': maintenance_records,
        'alerts': alerts,
        'maintenance_prediction': maintenance_prediction,
        'failure_prediction': failure_prediction,
    }

    return render(request, 'core/vehicle_detail.html', context)


# ===============================
# Analytics Views
# ===============================

def analytics(request):
    """
    AI-powered analytics view with predictions
    """
    ai = PredictiveMaintenanceAI()

    # Get predictions for all vehicles
    all_predictions = []
    for vehicle in Vehicle.objects.filter(status='active'):
        prediction = ai.predict_next_maintenance_mileage(vehicle)
        failure_pred = ai.predict_failure_probability(vehicle)

        all_predictions.append({
            'vehicle': vehicle,
            'maintenance_prediction': prediction,
            'failure_prediction': failure_pred,
        })

    # Get efficiency ratings
    efficiency_ratings = CostOptimizer.calculate_efficiency_ratings()

    # Get usage statistics
    usage_stats = FleetAnalytics.calculate_usage_stats()

    # Calculate average fleet metrics
    avg_fuel_efficiency = 0
    avg_cost_per_mile = 0

    if efficiency_ratings:
        avg_fuel_efficiency = sum(v['fuel_efficiency'] for v in efficiency_ratings) / len(efficiency_ratings)
        avg_cost_per_mile = sum(v['cost_per_mile'] for v in efficiency_ratings if v['cost_per_mile'] > 0) / len([v for v in efficiency_ratings if v['cost_per_mile'] > 0])

    # High-risk vehicles
    high_risk_vehicles = [
        p for p in all_predictions
        if p['failure_prediction']['risk_level'] in ['critical', 'high']
    ]

    # Vehicles needing immediate maintenance
    immediate_maintenance = [
        p for p in all_predictions
        if p['maintenance_prediction']['urgency'] in ['critical', 'high']
    ]

    # Top performing vehicles
    top_performers = efficiency_ratings[:5] if efficiency_ratings else []

    # Underperforming vehicles
    underperformers = efficiency_ratings[-5:] if efficiency_ratings else []

    context = {
        'page_title': 'Fleet Analytics',
        'predictions': all_predictions,
        'efficiency_ratings': efficiency_ratings,
        'usage_stats': usage_stats,
        'avg_fuel_efficiency': round(avg_fuel_efficiency, 2),
        'avg_cost_per_mile': round(avg_cost_per_mile, 2),
        'high_risk_vehicles': high_risk_vehicles,
        'immediate_maintenance': immediate_maintenance,
        'top_performers': top_performers,
        'underperformers': underperformers,
    }

    return render(request, 'core/analytics.html', context)


# ===============================
# Report View (CSV Export)
# ===============================

def export_report(request):
    """
    Export fleet performance data to CSV
    """
    # Get report type from query params
    report_type = request.GET.get('type', 'fleet')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="fleet_report_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)

    if report_type == 'fleet':
        # Fleet overview report
        writer.writerow([
            'Plate', 'VIN', 'Make', 'Model', 'Year', 'Type', 'Status',
            'Current Mileage', 'Total Distance', 'Fuel Efficiency (MPG)',
            'Cost per Mile ($)', 'Total Maintenance Cost ($)', 'Active Alerts'
        ])

        for vehicle in Vehicle.objects.all():
            writer.writerow([
                vehicle.plate,
                vehicle.vin,
                vehicle.make,
                vehicle.model,
                vehicle.year,
                vehicle.get_vehicle_type_display(),
                vehicle.get_status_display(),
                vehicle.current_mileage,
                round(vehicle.total_distance, 2),
                vehicle.fuel_efficiency,
                vehicle.cost_per_mile,
                round(vehicle.total_maintenance_cost, 2),
                vehicle.active_alerts_count,
            ])

    elif report_type == 'trips':
        # Trips report
        writer.writerow([
            'Vehicle', 'Driver', 'Start Date', 'End Date', 'Distance (miles)',
            'Fuel Used (gallons)', 'Fuel Efficiency (MPG)', 'Status', 'Start Location', 'End Location'
        ])

        trips = Trip.objects.select_related('vehicle', 'driver').order_by('-start_date')
        for trip in trips:
            writer.writerow([
                trip.vehicle.plate,
                trip.driver.name,
                trip.start_date.strftime('%Y-%m-%d %H:%M'),
                trip.end_date.strftime('%Y-%m-%d %H:%M') if trip.end_date else 'N/A',
                trip.distance,
                trip.fuel_used,
                trip.fuel_efficiency,
                trip.get_status_display(),
                trip.start_location,
                trip.end_location,
            ])

    elif report_type == 'maintenance':
        # Maintenance report
        writer.writerow([
            'Vehicle', 'Date', 'Type', 'Mileage at Service', 'Cost ($)',
            'Severity', 'Description', 'Performed By'
        ])

        records = MaintenanceRecord.objects.select_related('vehicle').order_by('-date')
        for record in records:
            writer.writerow([
                record.vehicle.plate,
                record.date.strftime('%Y-%m-%d %H:%M'),
                record.get_maintenance_type_display(),
                record.mileage_at_service,
                record.cost,
                record.get_severity_display(),
                record.description,
                record.performed_by,
            ])

    elif report_type == 'analytics':
        # Analytics report with predictions
        ai = PredictiveMaintenanceAI()

        writer.writerow([
            'Plate', 'Make/Model', 'Current Mileage', 'Predicted Next Maintenance Mileage',
            'Miles Until Maintenance', 'Failure Probability', 'Risk Level', 'Urgency', 'Confidence'
        ])

        for vehicle in Vehicle.objects.filter(status='active'):
            prediction = ai.predict_next_maintenance_mileage(vehicle)
            failure_pred = ai.predict_failure_probability(vehicle)

            writer.writerow([
                vehicle.plate,
                f"{vehicle.make} {vehicle.model}",
                vehicle.current_mileage,
                prediction['predicted_next_maintenance_mileage'],
                prediction['miles_until_maintenance'],
                f"{failure_pred['failure_probability'] * 100}%",
                failure_pred['risk_level'],
                prediction['urgency'],
                f"{prediction['confidence'] * 100}%",
            ])

    return response


def report_view(request):
    """
    Display report generation options
    """
    # Get summary statistics
    total_vehicles = Vehicle.objects.count()
    total_trips = Trip.objects.count()
    total_maintenance = MaintenanceRecord.objects.count()

    context = {
        'page_title': 'Reports',
        'total_vehicles': total_vehicles,
        'total_trips': total_trips,
        'total_maintenance': total_maintenance,
    }

    return render(request, 'core/report.html', context)


# ===============================
# AJAX/API Views
# ===============================

def refresh_alerts(request):
    """
    Refresh alerts using AI prediction (AJAX endpoint)
    """
    if request.method == 'POST':
        generator = AlertGenerator()
        new_alerts = generator.generate_maintenance_alerts()

        return JsonResponse({
            'success': True,
            'new_alerts': new_alerts,
            'message': f'Generated {new_alerts} new alerts.'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def get_vehicle_stats(request, vehicle_id):
    """
    Get real-time statistics for a vehicle (AJAX endpoint)
    """
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    ai = PredictiveMaintenanceAI()
    prediction = ai.predict_next_maintenance_mileage(vehicle)
    failure_pred = ai.predict_failure_probability(vehicle)

    stats = {
        'plate': vehicle.plate,
        'current_mileage': float(vehicle.current_mileage),
        'total_distance': float(vehicle.total_distance),
        'fuel_efficiency': vehicle.fuel_efficiency,
        'cost_per_mile': vehicle.cost_per_mile,
        'active_alerts': vehicle.active_alerts_count,
        'miles_until_maintenance': prediction['miles_until_maintenance'],
        'failure_probability': failure_pred['failure_probability'],
        'risk_level': failure_pred['risk_level'],
    }

    return JsonResponse(stats)


def dismiss_alert(request, alert_id):
    """
    Dismiss an alert (AJAX endpoint)
    """
    if request.method == 'POST':
        alert = get_object_or_404(Alert, id=alert_id)
        alert.resolve()

        return JsonResponse({
            'success': True,
            'message': 'Alert dismissed successfully.'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# ===============================
# Index View
# ===============================

def index(request):
    """
    Redirect to dashboard
    """
    return redirect('core:dashboard')
