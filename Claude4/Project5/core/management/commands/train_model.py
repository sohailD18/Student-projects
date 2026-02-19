"""
Django management command to train the AI model for travel time prediction.
Generates dummy training data and saves the trained model.
"""
import os
import csv
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate dummy trip data and train the AI travel time prediction model'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting AI model training process...'))

        # 1. Generate dummy training data
        self.stdout.write('Generating dummy training data...')
        df = self.generate_dummy_data(num_samples=5000)

        # Save the training data to CSV for reference
        csv_path = os.path.join(settings.BASE_DIR, 'training_data.csv')
        df.to_csv(csv_path, index=False)
        self.stdout.write(self.style.SUCCESS(f'Training data saved to: {csv_path}'))

        # 2. Prepare features and target
        self.stdout.write('Preparing features for training...')
        X, y = self.prepare_features(df)

        # 3. Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.stdout.write(f'Training set size: {len(X_train)}')
        self.stdout.write(f'Test set size: {len(X_test)}')

        # 4. Train the model
        self.stdout.write('Training RandomForestRegressor model...')
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        # 5. Evaluate the model
        self.stdout.write('Evaluating model performance...')
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        self.stdout.write(self.style.SUCCESS(f'Model Performance Metrics:'))
        self.stdout.write(f'  Mean Absolute Error: {mae:.2f} minutes')
        self.stdout.write(f'  Root Mean Squared Error: {rmse:.2f} minutes')
        self.stdout.write(f'  R² Score: {r2:.4f}')

        # 6. Save the model
        model_path = os.path.join(settings.BASE_DIR, 'travel_model.pkl')
        joblib.dump(model, model_path)
        self.stdout.write(self.style.SUCCESS(f'Model saved to: {model_path}'))

        # 7. Save feature names for consistent prediction
        feature_names = ['distance_km', 'traffic_level', 'weather_encoded', 'transport_mode_encoded']
        feature_path = os.path.join(settings.BASE_DIR, 'model_features.pkl')
        joblib.dump(feature_names, feature_path)
        self.stdout.write(self.style.SUCCESS(f'Feature names saved to: {feature_path}'))

        self.stdout.write(self.style.SUCCESS('✓ Model training completed successfully!'))

        # Show feature importance
        self.stdout.write('\nFeature Importance:')
        for feature, importance in zip(feature_names, model.feature_importances_):
            self.stdout.write(f'  {feature}: {importance:.4f}')

    def generate_dummy_data(self, num_samples=5000):
        """
        Generate realistic dummy trip data for training.
        Simulates various scenarios based on distance, traffic, weather, and transport mode.
        """
        data = []

        # Indian cities with approximate coordinates (for diversity)
        cities = [
            ('Delhi', 28.6139, 77.2090),
            ('Mumbai', 19.0760, 72.8777),
            ('Bangalore', 12.9716, 77.5946),
            ('Chennai', 13.0827, 80.2707),
            ('Kolkata', 22.5726, 88.3639),
            ('Hyderabad', 17.3850, 78.4867),
            ('Pune', 18.5204, 73.8567),
            ('Ahmedabad', 23.0225, 72.5714),
            ('Jaipur', 26.9124, 75.7873),
            ('Lucknow', 26.8467, 80.9462),
        ]

        transport_modes = ['car', 'bike', 'bus']
        weather_conditions = ['clear', 'cloudy', 'rain', 'heavy_rain', 'fog']

        for i in range(num_samples):
            # Random source and destination
            source_city, src_lat, src_lon = random.choice(cities)
            dest_city, dest_lat, dest_lon = random.choice(cities)

            # Ensure source != destination
            while dest_city == source_city:
                dest_city, dest_lat, dest_lon = random.choice(cities)

            # Calculate distance (simplified)
            distance = self.calculate_distance(src_lat, src_lon, dest_lat, dest_lon)

            # Only include reasonable distances (10km to 1500km)
            if distance < 10 or distance > 1500:
                continue

            # Traffic level (1-10, with weighted probability for moderate traffic)
            traffic_level = random.choices(
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                weights=[5, 10, 15, 25, 20, 12, 7, 4, 2, 1]  # More moderate traffic
            )[0]

            # Weather condition
            weather = random.choice(weather_conditions)

            # Transport mode
            transport = random.choice(transport_modes)

            # Calculate realistic travel time based on factors
            base_speed = {
                'car': 50,    # km/h average city speed
                'bike': 45,   # km/h
                'bus': 40,    # km/h
            }

            # Adjust speed based on traffic
            traffic_factor = 1 - (traffic_level - 1) * 0.08  # 1.0 to 0.28
            speed = base_speed[transport] * traffic_factor

            # Adjust for weather
            weather_penalty = {
                'clear': 1.0,
                'cloudy': 1.0,
                'rain': 1.15,
                'heavy_rain': 1.35,
                'fog': 1.25,
            }
            speed = speed / weather_penalty[weather]

            # Calculate time in minutes
            travel_time = (distance / speed) * 60

            # Add some random variation (+/- 10%)
            variation = random.uniform(0.9, 1.1)
            travel_time = travel_time * variation

            # Fuel cost estimation (INR)
            # Car: ~8 km/L, Bike: ~45 km/L, Bus: ~5 km/L
            fuel_efficiency = {'car': 8, 'bike': 45, 'bus': 5}
            fuel_price = 100  # per liter
            fuel_cost = (distance / fuel_efficiency[transport]) * fuel_price

            # Generate random date within last year
            days_ago = random.randint(0, 365)
            travel_date = datetime.now() - timedelta(days=days_ago)

            data.append({
                'distance_km': round(distance, 2),
                'traffic_level': traffic_level,
                'weather': weather,
                'transport_mode': transport,
                'travel_time_mins': round(travel_time, 2),
                'fuel_cost': round(fuel_cost, 2),
                'source_city': source_city,
                'dest_city': dest_city,
            })

        return pd.DataFrame(data)

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        from math import radians, cos, sin, asin, sqrt

        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r

    def prepare_features(self, df):
        """
        Prepare features for model training.
        Encodes categorical variables and creates feature matrix.
        """
        # Encode weather conditions
        weather_mapping = {'clear': 0, 'cloudy': 1, 'rain': 2, 'heavy_rain': 3, 'fog': 4}
        df['weather_encoded'] = df['weather'].map(weather_mapping)

        # Encode transport modes
        transport_mapping = {'car': 0, 'bike': 1, 'bus': 2}
        df['transport_mode_encoded'] = df['transport_mode'].map(transport_mapping)

        # Select features
        feature_columns = [
            'distance_km',
            'traffic_level',
            'weather_encoded',
            'transport_mode_encoded'
        ]

        X = df[feature_columns].values
        y = df['travel_time_mins'].values

        return X, y
