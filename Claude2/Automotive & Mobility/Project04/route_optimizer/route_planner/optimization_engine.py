"""
AI Optimization Engine for Route Planning
Implements heuristic algorithms for intelligent route optimization
"""

import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json


class RouteOptimizer:
    """
    AI-powered route optimization engine using heuristic algorithms
    """

    # Constants for calculations
    AVG_SPEED_KMH = 60.0
    FUEL_CONSUMPTION_L_PER_100KM = 8.5
    FUEL_PRICE_PER_LITER = 3.5  # USD
    CO2_PER_LITER = 2.31  # kg

    def __init__(self):
        self.current_hour = datetime.now().hour
        self.current_day = datetime.now().weekday()

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on Earth
        Returns distance in kilometers
        """
        # Convert latitude and longitude to radians
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in kilometers
        r = 6371
        return c * r

    def simulate_traffic_factor(self, distance_km: float, base_time_minutes: int) -> float:
        """
        Simulate traffic conditions based on time of day and day of week
        Returns a multiplier (1.0 = normal traffic, >1 = congestion)
        """
        # Base traffic patterns
        hour_factor = 1.0
        day_factor = 1.0

        # Rush hour multipliers (7-9 AM, 5-7 PM on weekdays)
        if self.current_day < 5:  # Monday-Friday
            if 7 <= self.current_hour <= 9 or 17 <= self.current_hour <= 19:
                hour_factor = random.uniform(1.8, 2.5)
            elif 10 <= self.current_hour <= 16:
                hour_factor = random.uniform(1.2, 1.5)
            elif 20 <= self.current_hour <= 22:
                hour_factor = random.uniform(1.1, 1.3)
        else:  # Weekend
            hour_factor = random.uniform(0.9, 1.2)

        # Add some randomness to simulate real-time conditions
        random_variation = random.uniform(0.9, 1.1)

        traffic_factor = hour_factor * day_factor * random_variation
        return max(0.8, min(traffic_factor, 3.0))  # Clamp between 0.8 and 3.0

    def calculate_estimated_time(self, distance_km: float, traffic_factor: float = 1.0) -> int:
        """
        Calculate estimated travel time based on distance and traffic
        Returns time in minutes
        """
        base_time = (distance_km / self.AVG_SPEED_KMH) * 60  # minutes
        adjusted_time = base_time * traffic_factor
        return int(round(adjusted_time))

    def calculate_fuel_cost(self, distance_km: float) -> float:
        """
        Calculate estimated fuel cost for a route
        Returns cost in USD
        """
        fuel_needed = (distance_km / 100) * self.FUEL_CONSUMPTION_L_PER_100KM
        cost = fuel_needed * self.FUEL_PRICE_PER_LITER
        return round(cost, 2)

    def calculate_co2_emission(self, distance_km: float) -> float:
        """
        Calculate CO2 emissions for a route
        Returns emissions in kg
        """
        fuel_needed = (distance_km / 100) * self.FUEL_CONSUMPTION_L_PER_100KM
        emissions = fuel_needed * self.CO2_PER_LITER
        return round(emissions, 2)

    def generate_waypoints(self, origin_lat: float, origin_lng: float,
                          dest_lat: float, dest_lng: float,
                          num_waypoints: int = 5) -> List[List[float]]:
        """
        Generate waypoints between origin and destination for route visualization
        Returns list of [lat, lng] pairs
        """
        waypoints = [[origin_lat, origin_lng]]

        # Generate intermediate waypoints with slight variations
        for i in range(1, num_waypoints):
            ratio = i / num_waypoints

            # Linear interpolation with added randomness for route variation
            lat = origin_lat + (dest_lat - origin_lat) * ratio
            lng = origin_lng + (dest_lng - origin_lng) * ratio

            # Add slight randomness to create realistic route variations
            lat += random.uniform(-0.02, 0.02)
            lng += random.uniform(-0.02, 0.02)

            waypoints.append([round(lat, 6), round(lng, 6)])

        waypoints.append([dest_lat, dest_lng])
        return waypoints

    def generate_route_variations(self, origin_lat: float, origin_lng: float,
                                  dest_lat: float, dest_lng: float) -> Dict:
        """
        Generate multiple route options (Fastest, Shortest, Scenic, Eco)
        Returns a dictionary with all route options
        """
        base_distance = self.haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)

        # Generate route options
        routes = {
            'fastest': self._generate_fastest_route(origin_lat, origin_lng, dest_lat, dest_lng, base_distance),
            'shortest': self._generate_shortest_route(origin_lat, origin_lng, dest_lat, dest_lng, base_distance),
            'scenic': self._generate_scenic_route(origin_lat, origin_lng, dest_lat, dest_lng, base_distance),
            'eco': self._generate_eco_route(origin_lat, origin_lng, dest_lat, dest_lng, base_distance),
        }

        # Determine recommended route
        recommended = self._select_recommended_route(routes)
        routes[recommended]['is_recommended'] = True

        # Add metadata
        routes['metadata'] = {
            'optimization_score': self._calculate_optimization_score(routes),
            'total_options': 4,
            'current_hour': self.current_hour,
            'current_day': self.current_day,
        }

        return routes

    def _generate_fastest_route(self, origin_lat: float, origin_lng: float,
                                dest_lat: float, dest_lng: float,
                                base_distance: float) -> Dict:
        """Generate fastest route (considering traffic)"""
        traffic_factor = self.simulate_traffic_factor(base_distance, 0)
        # Faster route may be slightly longer but avoids traffic
        distance = base_distance * random.uniform(1.0, 1.15)
        time = self.calculate_estimated_time(distance, traffic_factor)

        return {
            'type': 'fastest',
            'name': 'Fastest Route',
            'distance_km': round(distance, 2),
            'estimated_time_minutes': time,
            'traffic_factor': round(traffic_factor, 2),
            'fuel_cost': self.calculate_fuel_cost(distance),
            'co2_emission_kg': self.calculate_co2_emission(distance),
            'coordinates': self.generate_waypoints(origin_lat, origin_lng, dest_lat, dest_lng, 8),
            'is_recommended': False,
            'description': 'Optimized for minimal travel time considering current traffic',
            'color': '#2563eb'  # Blue
        }

    def _generate_shortest_route(self, origin_lat: float, origin_lng: float,
                                 dest_lat: float, dest_lng: float,
                                 base_distance: float) -> Dict:
        """Generate shortest distance route"""
        distance = base_distance  # Direct distance
        time = self.calculate_estimated_time(distance, 1.0)

        return {
            'type': 'shortest',
            'name': 'Shortest Route',
            'distance_km': round(distance, 2),
            'estimated_time_minutes': time,
            'traffic_factor': 1.0,
            'fuel_cost': self.calculate_fuel_cost(distance),
            'co2_emission_kg': self.calculate_co2_emission(distance),
            'coordinates': self.generate_waypoints(origin_lat, origin_lng, dest_lat, dest_lng, 5),
            'is_recommended': False,
            'description': 'Minimal distance route',
            'color': '#16a34a'  # Green
        }

    def _generate_scenic_route(self, origin_lat: float, origin_lng: float,
                               dest_lat: float, dest_lng: float,
                               base_distance: float) -> Dict:
        """Generate scenic route (longer but more enjoyable)"""
        distance = base_distance * random.uniform(1.2, 1.5)
        time = self.calculate_estimated_time(distance, 0.85)  # Lower traffic on scenic roads

        return {
            'type': 'scenic',
            'name': 'Most Scenic Route',
            'distance_km': round(distance, 2),
            'estimated_time_minutes': time,
            'traffic_factor': 0.85,
            'fuel_cost': self.calculate_fuel_cost(distance),
            'co2_emission_kg': self.calculate_co2_emission(distance),
            'coordinates': self.generate_waypoints(origin_lat, origin_lng, dest_lat, dest_lng, 12),
            'is_recommended': False,
            'description': 'Scenic route with beautiful views',
            'color': '#9333ea'  # Purple
        }

    def _generate_eco_route(self, origin_lat: float, origin_lng: float,
                           dest_lat: float, dest_lng: float,
                           base_distance: float) -> Dict:
        """Generate eco-friendly route"""
        distance = base_distance * random.uniform(1.05, 1.15)
        time = self.calculate_estimated_time(distance, 0.9)  # Steady speeds

        return {
            'type': 'eco',
            'name': 'Eco-Friendly Route',
            'distance_km': round(distance, 2),
            'estimated_time_minutes': time,
            'traffic_factor': 0.9,
            'fuel_cost': self.calculate_fuel_cost(distance),
            'co2_emission_kg': self.calculate_co2_emission(distance),
            'coordinates': self.generate_waypoints(origin_lat, origin_lng, dest_lat, dest_lng, 7),
            'is_recommended': False,
            'description': 'Optimized for fuel efficiency and lower emissions',
            'color': '#059669'  # Emerald
        }

    def _select_recommended_route(self, routes: Dict) -> str:
        """
        Select the best route based on weighted criteria
        Returns the route type key
        """
        scores = {}

        for route_type, route in routes.items():
            if route_type == 'metadata':
                continue

            # Weighted score calculation
            # Lower is better for time and cost, so we invert
            time_score = 100 / (route['estimated_time_minutes'] + 1)
            distance_score = 100 / (route['distance_km'] + 1)
            eco_score = 100 - route['co2_emission_kg']

            # Combined weighted score
            scores[route_type] = (time_score * 0.5 + distance_score * 0.3 + eco_score * 0.2)

        return max(scores.items(), key=lambda x: x[1])[0]

    def _calculate_optimization_score(self, routes: Dict) -> float:
        """
        Calculate overall optimization score (0-100)
        Based on improvement over baseline
        """
        if not routes:
            return 0.0

        # Use shortest route as baseline
        shortest = routes.get('shortest', {})
        if not shortest:
            return 0.0

        baseline_time = shortest.get('estimated_time_minutes', 60)
        fastest = routes.get('fastest', {})
        fastest_time = fastest.get('estimated_time_minutes', baseline_time)

        # Calculate time savings percentage
        time_saved = baseline_time - fastest_time
        score = min(100, max(0, (time_saved / baseline_time) * 100))

        return round(score, 2)


class AnalyticsEngine:
    """
    Analytics engine for route statistics and insights
    """

    def generate_hourly_traffic_pattern(self) -> List[Dict]:
        """Generate hourly traffic pattern for charts"""
        hours = list(range(24))
        traffic_data = []

        for hour in hours:
            # Simulate traffic patterns
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                traffic = random.randint(70, 100)
            elif 10 <= hour <= 16:
                traffic = random.randint(40, 70)
            elif 20 <= hour <= 22:
                traffic = random.randint(30, 50)
            else:
                traffic = random.randint(10, 30)

            traffic_data.append({
                'hour': f"{hour}:00",
                'traffic_level': traffic
            })

        return traffic_data

    def generate_weekly_comparison(self) -> List[Dict]:
        """Generate weekly route efficiency comparison"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        data = []

        for day in days:
            data.append({
                'day': day,
                'avg_time_minutes': random.randint(25, 45),
                'avg_distance_km': random.randint(15, 35),
                'fuel_savings_percent': random.randint(5, 20)
            })

        return data

    def generate_route_type_distribution(self) -> List[Dict]:
        """Generate distribution of route types selected"""
        return [
            {'route_type': 'Fastest', 'count': random.randint(40, 60), 'color': '#2563eb'},
            {'route_type': 'Shortest', 'count': random.randint(20, 35), 'color': '#16a34a'},
            {'route_type': 'Scenic', 'count': random.randint(10, 25), 'color': '#9333ea'},
            {'route_type': 'Eco-Friendly', 'count': random.randint(15, 30), 'color': '#059669'},
        ]

    def generate_efficiency_trend(self, days: int = 30) -> List[Dict]:
        """Generate efficiency trend over time"""
        data = []
        base_date = datetime.now() - timedelta(days=days)

        for i in range(days):
            date = base_date + timedelta(days=i)
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'optimization_score': random.randint(60, 95),
                'time_saved_minutes': random.randint(5, 25),
                'cost_saved_usd': round(random.uniform(1.5, 8.5), 2)
            })

        return data
