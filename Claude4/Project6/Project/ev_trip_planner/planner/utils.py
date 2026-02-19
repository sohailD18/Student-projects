"""
EV Trip Planning Utilities

This module contains algorithms and utilities for calculating routes,
battery consumption, and charging stops.
"""

import math
from core.models import Vehicle, ChargingStation


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers
    r = 6371
    return c * r


def calculate_battery_consumption(vehicle, distance_km, elevation_gain=0):
    """
    Calculate estimated battery consumption for a trip

    Args:
        vehicle: Vehicle instance
        distance_km: Distance of trip in kilometers
        elevation_gain: Elevation gain in meters (optional)

    Returns:
        Battery consumption in kWh
    """
    # Base consumption: Use ~5.5 km per kWh (typical for Indian EVs)
    efficiency = 5.5  # km per kWh

    # Adjust for vehicle specs if available
    if vehicle.range_km and vehicle.battery_capacity:
        efficiency = vehicle.range_km / vehicle.battery_capacity

    # Calculate base consumption
    consumption = distance_km / efficiency

    # Add elevation factor (approximate: 300m elevation gain = 10% more consumption)
    if elevation_gain > 0:
        elevation_factor = 1 + (elevation_gain / 3000)
        consumption *= elevation_factor

    # Add weather/speed buffer (10%)
    consumption *= 1.10

    return round(consumption, 2)


def calculate_charging_time(kwh_needed, charging_power_kw):
    """
    Calculate estimated charging time

    Args:
        kwh_needed: Amount of energy needed in kWh
        charging_power_kw: Charging power in kW

    Returns:
        Charging time in minutes
    """
    if charging_power_kw <= 0:
        return 0

    hours = kwh_needed / charging_power_kw
    minutes = hours * 60

    # Add buffer for charging curve (batteries charge slower at high percentages)
    minutes *= 1.2

    return int(round(minutes))


def find_charging_stations_along_route(start_lat, start_lng, end_lat, end_lng, vehicle_range, max_stations=5):
    """
    Find charging stations along a route (simplified - in reality would use routing API)

    Args:
        start_lat, start_lng: Starting coordinates
        end_lat, end_lng: Ending coordinates
        vehicle_range: Vehicle's range in kilometers on full charge
        max_stations: Maximum number of stations to suggest

    Returns:
        List of charging stations with distance from start
    """
    all_stations = ChargingStation.objects.filter(is_available=True)

    # Calculate total distance
    total_distance = haversine_distance(start_lat, start_lng, end_lat, end_lng)

    # Find stations that are somewhat along the route
    stations_along_route = []

    for station in all_stations:
        # Distance from start to station
        dist_to_station = haversine_distance(start_lat, start_lng, station.latitude, station.longitude)

        # Distance from station to end
        dist_from_station = haversine_distance(station.latitude, station.longitude, end_lat, end_lng)

        # Check if station is reasonable (not too far off route)
        # Using triangle inequality: station should be on or near direct path
        if dist_to_station + dist_from_station <= total_distance * 1.3:  # 30% detour tolerance
            # Check if we'd need to charge before this point
            stations_along_route.append({
                'station': station,
                'distance_from_start': dist_to_station,
                'distance_to_end': dist_from_station,
            })

    # Sort by distance from start
    stations_along_route.sort(key=lambda x: x['distance_from_start'])

    # Determine where charging is needed
    needed_stops = []
    current_range_km = vehicle_range * 0.8  # Use 80% of actual range as safety margin

    for station_data in stations_along_route:
        if station_data['distance_from_start'] >= current_range_km:
            # We need to stop here or before
            needed_stops.append(station_data)
            current_range_km = station_data['distance_from_start'] + (vehicle_range * 0.8)

            if len(needed_stops) >= max_stations:
                break

    # If we can't make the destination without charging, add stops
    if needed_stops:
        last_stop_distance = needed_stops[-1]['distance_from_start']
        remaining_distance = total_distance - last_stop_distance
        if remaining_distance > vehicle_range * 0.8:
            # Need more stops (simplified logic)
            pass

    return needed_stops[:max_stations]


def plan_trip(start_location, destination, vehicle, initial_battery, start_coords=None, end_coords=None):
    """
    Main trip planning function

    Args:
        start_location: Starting location name
        destination: Destination name
        vehicle: Vehicle instance
        initial_battery: Initial battery percentage (0-100)
        start_coords: Tuple of (lat, lng) for start (optional)
        end_coords: Tuple of (lat, lng) for end (optional)

    Returns:
        Dictionary with trip plan including route, consumption, and charging stops
    """
    # Mock coordinates if not provided (in production, use geocoding API)
    if not start_coords:
        # Use default coordinates for India/Karnataka
        start_coords = (12.9716, 77.5946)  # Bangalore default
    if not end_coords:
        end_coords = (12.3119, 76.6524)  # Mysore default

    start_lat, start_lng = start_coords
    end_lat, end_lng = end_coords

    # Calculate distance
    distance = haversine_distance(start_lat, start_lng, end_lat, end_lng)

    # Calculate battery consumption
    consumption = calculate_battery_consumption(vehicle, distance)

    # Calculate battery percentages
    initial_kwh = (initial_battery / 100) * vehicle.battery_capacity
    remaining_kwh = initial_kwh - consumption
    final_battery = max(0, (remaining_kwh / vehicle.battery_capacity) * 100)

    # Calculate duration (average 60 km/h for Indian highways)
    duration_minutes = int((distance / 60) * 60)

    # Find charging stops if needed
    vehicle_range = vehicle.range_km
    charging_stops = []

    if final_battery < 20:  # Need charging if final battery below 20%
        suggested_stops = find_charging_stations_along_route(
            start_lat, start_lng, end_lat, end_lng, vehicle_range
        )

        # Calculate charging details for each stop
        current_battery = initial_battery
        accumulated_distance = 0

        for i, stop_data in enumerate(suggested_stops):
            station = stop_data['station']
            dist_to_stop = stop_data['distance_from_start'] - accumulated_distance

            # Battery needed to reach this stop
            kwh_to_stop = calculate_battery_consumption(vehicle, dist_to_stop)
            battery_at_stop = current_battery - ((kwh_to_stop / vehicle.battery_capacity) * 100)

            if battery_at_stop < 20:  # Need to charge
                # Charge to 80%
                kwh_needed = (80 - battery_at_stop) / 100 * vehicle.battery_capacity
                charge_time = calculate_charging_time(kwh_needed, station.power_kw)
                charge_cost = kwh_needed * float(station.price_per_kwh)

                charging_stops.append({
                    'station': station,
                    'stop_number': i + 1,
                    'battery_before': round(max(0, battery_at_stop), 1),
                    'battery_after': 80,
                    'charge_time': charge_time,
                    'charge_cost': round(charge_cost, 2),
                    'kwh_needed': round(kwh_needed, 2),
                })

                current_battery = 80
                accumulated_distance = stop_data['distance_from_start']

    return {
        'distance': round(distance, 2),
        'duration': duration_minutes,
        'consumption': consumption,
        'initial_battery': initial_battery,
        'final_battery': round(final_battery, 1),
        'charging_stops': charging_stops,
        'total_charging_cost': sum(stop['charge_cost'] for stop in charging_stops),
        'total_charging_time': sum(stop['charge_time'] for stop in charging_stops),
        'needs_charging': len(charging_stops) > 0,
    }


def get_route_polyline(start_lat, start_lng, end_lat, end_lng):
    """
    Generate a simple route polyline (in production, use routing API like OSRM)
    Returns list of (lat, lng) tuples
    """
    # Simple straight line with intermediate points
    num_points = 10
    points = []

    for i in range(num_points + 1):
        ratio = i / num_points
        lat = start_lat + (end_lat - start_lat) * ratio
        lng = start_lng + (end_lng - start_lng) * ratio
        points.append((lat, lng))

    return points
