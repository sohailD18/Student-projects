from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Trip, ChargingStop
from .forms import TripPlannerForm, TripNotesForm
from .utils import plan_trip, get_route_polyline
from core.models import Vehicle


# Simple coordinate mapping for Karnataka cities
KARNATAKA_CITIES = {
    'bangalore': (12.9716, 77.5946),
    'bengaluru': (12.9716, 77.5946),
    'mysore': (12.3119, 76.6524),
    'mysuru': (12.3119, 76.6524),
    'hubli': (15.3647, 75.1240),
    'hubballi': (15.3647, 75.1240),
    'mangalore': (12.9141, 74.8560),
    'mangaluru': (12.9141, 74.8560),
    'belagavi': (15.8481, 74.5129),
    'belgaum': (15.8481, 74.5129),
    'tumkur': (13.3392, 77.1130),
    'tumakuru': (13.3392, 77.1130),
    'shivamogga': (13.9287, 75.5679),
    'shimoga': (13.9287, 75.5679),
    'dharwad': (15.4579, 75.0078),
    'bellary': (15.1394, 76.9211),
    'ballari': (15.1394, 76.9211),
    'vijayapura': (16.8340, 75.7124),
    'bijapur': (16.8340, 75.7124),
    'kalaburagi': (17.3189, 76.8343),
    'gulbarga': (17.3189, 76.8343),
    'udupi': (13.3409, 74.7421),
    'chikmagalur': (13.3181, 75.7687),
    'chikkamagaluru': (13.3181, 75.7681),
    'hassan': (13.0073, 76.0986),
    'mandya': (12.5227, 76.8952),
    'chitradurga': (14.2265, 76.3946),
    'davanagere': (14.4667, 75.9258),
    'kolar': (13.1364, 78.1310),
    'raichur': (16.2076, 77.3463),
    'raichuru': (16.2076, 77.3463),
}


def get_coordinates(location_name):
    """
    Get coordinates for a location in Karnataka.
    Returns (lat, lng) tuple or defaults to Bangalore if not found.
    """
    location_lower = location_name.lower().strip()

    # Direct match
    if location_lower in KARNATAKA_CITIES:
        return KARNATAKA_CITIES[location_lower]

    # Partial match (e.g., "Bangalore, Karnataka" -> "bangalore")
    for city, coords in KARNATAKA_CITIES.items():
        if city in location_lower or location_lower in city:
            return coords

    # Default to Bangalore if not found
    return KARNATAKA_CITIES['bangalore']


def plan_trip_view(request):
    """Main trip planning view"""
    if request.method == 'POST':
        form = TripPlannerForm(request.user, request.POST)
        if form.is_valid():
            start_location = form.cleaned_data['start_location']
            destination = form.cleaned_data['destination']
            vehicle_id = form.cleaned_data['vehicle']
            battery_percent = form.cleaned_data['battery_percent']

            try:
                vehicle = Vehicle.objects.get(id=vehicle_id, user=request.user)

                # Get coordinates for the locations
                start_coords = get_coordinates(start_location)
                end_coords = get_coordinates(destination)

                # Plan the trip
                trip_plan = plan_trip(
                    start_location=start_location,
                    destination=destination,
                    vehicle=vehicle,
                    initial_battery=battery_percent,
                    start_coords=start_coords,
                    end_coords=end_coords
                )

                # Save the trip to database
                trip = Trip.objects.create(
                    user=request.user,
                    vehicle=vehicle,
                    start_location=start_location,
                    destination=destination,
                    start_lat=start_coords[0],
                    start_lng=start_coords[1],
                    destination_lat=end_coords[0],
                    destination_lng=end_coords[1],
                    estimated_distance=trip_plan['distance'],
                    estimated_duration=trip_plan['duration'],
                    battery_consumption=trip_plan['consumption'],
                    initial_battery_percent=battery_percent,
                    final_battery_percent=int(trip_plan['final_battery']),
                    status='planned'
                )

                # Save charging stops
                for stop_data in trip_plan['charging_stops']:
                    ChargingStop.objects.create(
                        trip=trip,
                        station=stop_data['station'],
                        stop_order=stop_data['stop_number'],
                        estimated_charge_time=stop_data['charge_time'],
                        estimated_cost=stop_data['charge_cost'],
                        battery_before_charge=stop_data['battery_before'],
                        battery_after_charge=stop_data['battery_after']
                    )

                # Get route polyline
                route_polyline = get_route_polyline(
                    start_coords[0], start_coords[1],
                    end_coords[0], end_coords[1]
                )

                # Format duration
                hours = trip_plan['duration'] // 60
                minutes = trip_plan['duration'] % 60
                trip_plan['formatted_duration'] = f"{hours}h {minutes}m"

                context = {
                    'trip': trip,
                    'trip_plan': trip_plan,
                    'route_polyline': route_polyline,
                    'form': form,
                }

                messages.success(request, 'Trip planned successfully!')
                return render(request, 'planner/trip_plan.html', context)

            except Vehicle.DoesNotExist:
                messages.error(request, 'Please select a valid vehicle.')
    else:
        form = TripPlannerForm(request.user)

    context = {
        'form': form,
    }
    return render(request, 'planner/plan_trip.html', context)


@login_required
def trip_history(request):
    """View trip history"""
    trips = request.user.trips.all()

    # Add formatted duration to each trip
    for trip in trips:
        hours = trip.estimated_duration // 60
        minutes = trip.estimated_duration % 60
        trip.formatted_duration = f"{hours}h {minutes}m"

    context = {
        'trips': trips,
    }
    return render(request, 'planner/trip_history.html', context)


@login_required
def trip_detail(request, pk):
    """View trip details"""
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    charging_stops = trip.charging_stops.all()

    # Format duration
    hours = trip.estimated_duration // 60
    minutes = trip.estimated_duration % 60
    trip.formatted_duration = f"{hours}h {minutes}m"

    context = {
        'trip': trip,
        'charging_stops': charging_stops,
    }
    return render(request, 'planner/trip_detail.html', context)


@login_required
def trip_update(request, pk):
    """Update trip notes and status"""
    trip = get_object_or_404(Trip, pk=pk, user=request.user)

    # Format duration
    hours = trip.estimated_duration // 60
    minutes = trip.estimated_duration % 60
    trip.formatted_duration = f"{hours}h {minutes}m"

    if request.method == 'POST':
        form = TripNotesForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trip updated successfully!')
            return redirect('trip_detail', pk=trip.pk)
    else:
        form = TripNotesForm(instance=trip)

    context = {
        'form': form,
        'trip': trip,
    }
    return render(request, 'planner/trip_update.html', context)


@login_required
def trip_delete(request, pk):
    """Delete a trip"""
    trip = get_object_or_404(Trip, pk=pk, user=request.user)

    if request.method == 'POST':
        trip.delete()
        messages.success(request, 'Trip deleted successfully!')
        return redirect('planner:trip_history')

    context = {
        'trip': trip,
    }
    return render(request, 'planner/trip_confirm_delete.html', context)


def trip_estimate_api(request):
    """API endpoint for quick trip estimation (AJAX)"""
    if request.method == 'GET':
        vehicle_id = request.GET.get('vehicle_id')
        distance = float(request.GET.get('distance', 100))  # Distance in km
        battery_percent = int(request.GET.get('battery_percent', 100))

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            # Consumption calculation: distance / (km per kWh) with 10% buffer
            efficiency = vehicle.range_km / vehicle.battery_capacity  # km per kWh
            consumption = (distance / efficiency) * 1.1
            remaining_kwh = (battery_percent / 100) * vehicle.battery_capacity - consumption
            final_battery = max(0, (remaining_kwh / vehicle.battery_capacity) * 100)

            return JsonResponse({
                'success': True,
                'consumption': round(consumption, 2),
                'final_battery': round(final_battery, 1),
                'needs_charging': final_battery < 20,
            })
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
