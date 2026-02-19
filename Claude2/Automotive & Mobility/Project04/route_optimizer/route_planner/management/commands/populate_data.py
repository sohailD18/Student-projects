"""
Management command to populate database with dummy data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from route_optimizer.route_planner.models import Location, TrafficData, Route, RouteHistory, OptimizationMetrics


class Command(BaseCommand):
    help = 'Populate database with dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate dummy data...'))

        # Clear existing data (optional - comment out if you want to keep existing data)
        # RouteHistory.objects.all().delete()
        # Route.objects.all().delete()
        # TrafficData.objects.all().delete()
        # Location.objects.all().delete()

        self.create_demo_users()
        self.create_locations()
        self.create_traffic_data()
        self.create_routes()
        self.create_route_history()
        self.create_optimization_metrics()

        self.stdout.write(self.style.SUCCESS('✅ Dummy data populated successfully!'))
        self.stdout.write(self.style.WARNING('\nDemo Credentials:'))
        self.stdout.write(self.style.WARNING('  Email: demo@example.com'))
        self.stdout.write(self.style.WARNING('  Password: demo123'))

    def create_demo_users(self):
        """Create demo users"""
        self.stdout.write('\n📝 Creating demo users...')

        users_data = [
            {
                'username': 'demo',
                'email': 'demo@example.com',
                'password': 'demo123',
                'first_name': 'Demo',
                'last_name': 'User'
            },
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_superuser': True,
                'is_staff': True
            },
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'john123',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'password': 'jane123',
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', '')
                )
                if user_data.get('is_superuser'):
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created user: {user.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⊙ User already exists: {user_data['username']}"))

    def create_locations(self):
        """Create dummy locations"""
        self.stdout.write('\n📍 Creating locations...')

        locations = [
            {'name': 'New York City', 'lat': 40.7128, 'lng': -74.0060, 'city': 'New York', 'address': 'Manhattan, NYC'},
            {'name': 'Los Angeles', 'lat': 34.0522, 'lng': -118.2437, 'city': 'Los Angeles', 'address': 'Downtown LA'},
            {'name': 'Chicago', 'lat': 41.8781, 'lng': -87.6298, 'city': 'Chicago', 'address': 'Loop District'},
            {'name': 'Houston', 'lat': 29.7604, 'lng': -95.3698, 'city': 'Houston', 'address': 'Downtown Houston'},
            {'name': 'Phoenix', 'lat': 33.4484, 'lng': -112.0740, 'city': 'Phoenix', 'address': 'Central Phoenix'},
            {'name': 'Philadelphia', 'lat': 39.9526, 'lng': -75.1652, 'city': 'Philadelphia', 'address': 'Center City'},
            {'name': 'San Antonio', 'lat': 29.4241, 'lng': -98.4936, 'city': 'San Antonio', 'address': 'Downtown SA'},
            {'name': 'San Diego', 'lat': 32.7157, 'lng': -117.1611, 'city': 'San Diego', 'address': 'Gaslamp Quarter'},
            {'name': 'Dallas', 'lat': 32.7767, 'lng': -96.7970, 'city': 'Dallas', 'address': 'Downtown Dallas'},
            {'name': 'San Jose', 'lat': 37.3382, 'lng': -121.8863, 'city': 'San Jose', 'address': 'Downtown San Jose'},
            {'name': 'Boston', 'lat': 42.3601, 'lng': -71.0589, 'city': 'Boston', 'address': 'Downtown Boston'},
            {'name': 'Miami', 'lat': 25.7617, 'lng': -80.1918, 'city': 'Miami', 'address': 'Downtown Miami'},
            {'name': 'Seattle', 'lat': 47.6062, 'lng': -122.3321, 'city': 'Seattle', 'address': 'Downtown Seattle'},
            {'name': 'Denver', 'lat': 39.7392, 'lng': -104.9903, 'city': 'Denver', 'address': 'Downtown Denver'},
            {'name': 'Atlanta', 'lat': 33.7490, 'lng': -84.3880, 'city': 'Atlanta', 'address': 'Downtown Atlanta'},
        ]

        for loc_data in locations:
            if not Location.objects.filter(name=loc_data['name']).exists():
                Location.objects.create(**loc_data)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created location: {loc_data['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⊙ Location already exists: {loc_data['name']}"))

    def create_traffic_data(self):
        """Create dummy traffic data"""
        self.stdout.write('\n🚦 Creating traffic data...')

        # Generate traffic data for different hours and days
        hours = list(range(24))
        days = list(range(1, 8))  # 1-7 (Monday-Sunday)

        count = 0
        for day in days:
            for hour in hours:
                segment_id = f"segment_day{day}_hour{hour}"

                if not TrafficData.objects.filter(segment_id=segment_id).exists():
                    # Simulate realistic traffic patterns
                    if day < 5:  # Weekdays
                        if 7 <= hour <= 9 or 17 <= hour <= 19:
                            traffic_level = random.uniform(1.8, 2.5)
                            avg_speed = random.uniform(25, 40)
                        elif 10 <= hour <= 16:
                            traffic_level = random.uniform(1.2, 1.5)
                            avg_speed = random.uniform(45, 55)
                        else:
                            traffic_level = random.uniform(0.9, 1.2)
                            avg_speed = random.uniform(55, 65)
                    else:  # Weekends
                        traffic_level = random.uniform(0.9, 1.3)
                        avg_speed = random.uniform(50, 65)

                    # Generate historical congestion data
                    historical = {
                        str(h): random.uniform(0.8, 2.0) for h in hours
                    }

                    TrafficData.objects.create(
                        segment_id=segment_id,
                        traffic_level=round(traffic_level, 2),
                        avg_speed=round(avg_speed, 2),
                        hour=hour,
                        day_of_week=day,
                        historical_congestion=historical
                    )
                    count += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {count} traffic data entries"))

    def create_routes(self):
        """Create dummy routes between locations"""
        self.stdout.write('\n🛣️ Creating routes...')

        locations = list(Location.objects.all())
        route_types = ['fastest', 'shortest', 'scenic', 'eco']

        count = 0
        # Create routes between random location pairs
        for i in range(min(50, len(locations) * 3)):
            origin = random.choice(locations)
            destination = random.choice(locations)

            if origin == destination:
                continue

            route_type = random.choice(route_types)

            # Calculate distance (simplified)
            distance = random.uniform(50, 500)

            # Generate route type characteristics
            if route_type == 'fastest':
                distance *= random.uniform(1.0, 1.15)
                traffic_factor = random.uniform(1.0, 1.5)
            elif route_type == 'shortest':
                traffic_factor = 1.0
            elif route_type == 'scenic':
                distance *= random.uniform(1.2, 1.5)
                traffic_factor = random.uniform(0.7, 0.9)
            else:  # eco
                distance *= random.uniform(1.05, 1.15)
                traffic_factor = random.uniform(0.85, 0.95)

            estimated_time = int((distance / 60) * 60 * traffic_factor)  # minutes
            fuel_cost = round((distance / 100) * 8.5 * 3.5, 2)
            co2_emission = round((distance / 100) * 8.5 * 2.31, 2)

            # Generate path coordinates
            path_coords = self._generate_path_coordinates(
                origin.latitude, origin.longitude,
                destination.latitude, destination.longitude
            )

            Route.objects.create(
                origin=origin,
                destination=destination,
                route_type=route_type,
                distance_km=round(distance, 2),
                estimated_time_minutes=estimated_time,
                path_coordinates=path_coords,
                traffic_factor=round(traffic_factor, 2),
                fuel_cost_estimate=fuel_cost,
                co2_emission_kg=co2_emission,
                is_recommended=(route_type == 'fastest' and random.random() > 0.5)
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {count} routes"))

    def _generate_path_coordinates(self, lat1, lng1, lat2, lng2):
        """Generate path coordinates for route visualization"""
        coords = [[lat1, lng1]]
        num_points = random.randint(5, 10)

        for i in range(1, num_points):
            ratio = i / num_points
            lat = lat1 + (lat2 - lat1) * ratio + random.uniform(-0.02, 0.02)
            lng = lng1 + (lng2 - lng1) * ratio + random.uniform(-0.02, 0.02)
            coords.append([round(lat, 6), round(lng, 6)])

        coords.append([lat2, lng2])
        return coords

    def create_route_history(self):
        """Create dummy route history"""
        self.stdout.write('\n📜 Creating route history...')

        users = list(User.objects.all())
        locations = list(Location.objects.all())
        route_types = ['fastest', 'shortest', 'scenic', 'eco']

        count = 0
        for i in range(30):
            origin = random.choice(locations)
            destination = random.choice(locations)

            if origin == destination:
                continue

            distance = random.uniform(50, 400)
            time = int(random.uniform(30, 300))

            # Generate available routes
            available_routes = {}
            for rt in route_types:
                available_routes[rt] = {
                    'type': rt,
                    'distance_km': round(distance * random.uniform(0.9, 1.3), 2),
                    'estimated_time_minutes': time,
                    'fuel_cost': round(distance * 0.3, 2),
                    'traffic_factor': round(random.uniform(0.8, 2.0), 2),
                    'is_recommended': rt == 'fastest'
                }

            selected_type = random.choice(route_types)
            selected_route = available_routes[selected_type]

            RouteHistory.objects.create(
                user=random.choice(users) if random.random() > 0.3 else None,
                origin_name=origin.name,
                origin_lat=origin.latitude,
                origin_lng=origin.longitude,
                destination_name=destination.name,
                destination_lat=destination.latitude,
                destination_lng=destination.longitude,
                selected_route_type=selected_type,
                distance_km=selected_route['distance_km'],
                estimated_time_minutes=selected_route['estimated_time_minutes'],
                fuel_cost=selected_route['fuel_cost'],
                available_routes=available_routes,
                optimization_score=random.uniform(50, 95),
                created_at=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {count} route history entries"))

    def create_optimization_metrics(self):
        """Create dummy optimization metrics"""
        self.stdout.write('\n📊 Creating optimization metrics...')

        for days_ago in range(30, 0, -1):
            date = datetime.now().date() - timedelta(days=days_ago)

            if not OptimizationMetrics.objects.filter(date=date).exists():
                OptimizationMetrics.objects.create(
                    date=date,
                    total_routes_calculated=random.randint(20, 100),
                    avg_optimization_time_ms=random.uniform(50, 200),
                    avg_savings_minutes=random.uniform(5, 25),
                    avg_cost_savings_usd=random.uniform(1.5, 10.0),
                    traffic_prediction_accuracy=random.uniform(75, 95),
                    daily_stats={
                        'hourly_traffic': [random.randint(10, 100) for _ in range(24)],
                        'route_distribution': {
                            'fastest': random.randint(30, 50),
                            'shortest': random.randint(15, 30),
                            'scenic': random.randint(10, 20),
                            'eco': random.randint(10, 25)
                        }
                    }
                )

        self.stdout.write(self.style.SUCCESS('  ✓ Created 30 days of optimization metrics'))
