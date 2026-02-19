"""
Machine Learning Training Script for Traffic Congestion Prediction

This script performs the following tasks:
1. Generates synthetic traffic data (1000+ records)
2. Preprocesses data (encoding, scaling)
3. Trains a RandomForestClassifier model
4. Saves the model and preprocessing artifacts

Usage:
    python train_model.py

Requirements:
    - pandas
    - scikit-learn
    - numpy
    - joblib
    - django (must be set up)

Author: BCA Final Year Project
Date: 2024
"""

import os
import sys
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# ==============================================================================
# DJANGO SETUP
# ==============================================================================

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffic_project.settings')

import django
django.setup()

from traffic_app.models import TrafficData


# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Synthetic data generation parameters
NUM_RECORDS = 1500  # Number of records to generate
START_DATE = datetime.now() - timedelta(days=90)  # Start 3 months ago
END_DATE = datetime.now()

# Locations from the model
LOCATIONS = [choice[0] for choice in TrafficData.LOCATION_CHOICES]

# Weather conditions
WEATHER_CONDITIONS = [choice[0] for choice in TrafficData.WEATHER_CHOICES]

# Congestion levels
CONGESTION_LEVELS = ['Low', 'Medium', 'High']

# Vehicle count ranges by time of day
VEHICLE_RANGES = {
    'night': (10, 50),      # 10 PM - 5 AM
    'morning_rush': (80, 200),  # 7 AM - 9 AM
    'day': (40, 120),       # 10 AM - 4 PM
    'evening_rush': (90, 220),  # 5 PM - 7 PM
    'evening': (30, 80),    # 8 PM - 9 PM
}


# ==============================================================================
# SYNTHETIC DATA GENERATION
# ==============================================================================

def generate_synthetic_data(num_records=NUM_RECORDS):
    """
    Generate synthetic traffic data for training the ML model.

    The data generation follows realistic traffic patterns:
    - Rush hours (7-9 AM, 5-7 PM) have higher vehicle counts
    - Weather affects congestion (Rainy = more congestion)
    - Weekends have different patterns than weekdays
    - Locations have varying baseline traffic levels

    Args:
        num_records: Number of records to generate

    Returns:
        pd.DataFrame: Synthetic traffic data with all features
    """
    print(f"Generating {num_records} synthetic traffic records...")

    data = []
    current_date = START_DATE

    # Location multipliers (some locations are busier)
    location_multipliers = {
        'Main Street Junction': 1.5,
        'Highway Exit 45': 1.8,
        'City Center Square': 2.0,
        'North Avenue Bridge': 1.3,
        'Market Street Crossing': 1.4,
        'Railway Road Intersection': 1.6,
        'University Gate': 1.2,
        'Hospital District': 1.1,
        'Industrial Area': 1.0,
        'Suburb Entrance': 0.9,
    }

    for i in range(num_records):
        # Generate random datetime
        random_minutes = random.randint(0, 59)
        random_hours = random.randint(0, 23)
        random_days = random.randint(0, (END_DATE - START_DATE).days)
        date_time = current_date + timedelta(
            days=random_days,
            hours=random_hours,
            minutes=random_minutes
        )

        # Select location
        location = random.choice(LOCATIONS)

        # Determine time period
        hour = date_time.hour
        if 22 <= hour or hour <= 5:
            time_period = 'night'
        elif 7 <= hour <= 9:
            time_period = 'morning_rush'
        elif 10 <= hour <= 16:
            time_period = 'day'
        elif 17 <= hour <= 19:
            time_period = 'evening_rush'
        else:
            time_period = 'evening'

        # Generate base vehicle count
        base_range = VEHICLE_RANGES[time_period]
        location_mult = location_multipliers.get(location, 1.0)

        # Weather factor
        weather = random.choice(WEATHER_CONDITIONS)
        weather_factor = 1.0
        if weather == 'Rainy':
            weather_factor = 1.2  # 20% more vehicles in rain
        elif weather == 'Cloudy':
            weather_factor = 1.05
        elif weather == 'Foggy':
            weather_factor = 0.9

        # Weekend factor
        is_weekend = date_time.weekday() >= 5
        weekend_factor = 0.7 if is_weekend else 1.0  # Less traffic on weekends

        # Calculate final vehicle count with some randomness
        vehicle_count = int(
            (random.uniform(*base_range) * location_mult * weather_factor * weekend_factor)
            + random.randint(-10, 10)
        )
        vehicle_count = max(5, vehicle_count)  # Minimum 5 vehicles

        # Determine congestion level based on rules
        # This creates labeled data for supervised learning
        if time_period == 'morning_rush' or time_period == 'evening_rush':
            if vehicle_count > 150 or (weather == 'Rainy' and vehicle_count > 120):
                congestion = 'High'
            elif vehicle_count > 100:
                congestion = 'Medium'
            else:
                congestion = 'Low'
        elif time_period == 'night':
            congestion = 'Low' if vehicle_count < 40 else 'Medium'
        else:  # day or evening
            if vehicle_count > 130 or (weather == 'Rainy' and vehicle_count > 100):
                congestion = 'High'
            elif vehicle_count > 80:
                congestion = 'Medium'
            else:
                congestion = 'Low'

        data.append({
            'date_time': date_time,
            'location': location,
            'vehicle_count': vehicle_count,
            'weather': weather,
            'congestion_level': congestion,
        })

    df = pd.DataFrame(data)
    print(f"Generated {len(df)} records successfully!")
    return df


# ==============================================================================
# DATA PREPROCESSING
# ==============================================================================

def preprocess_data(df):
    """
    Preprocess the traffic data for ML training.

    Steps:
    1. Extract temporal features (hour, day of week, weekend flag, rush hour flag)
    2. Encode categorical variables (location, weather, congestion_level)
    3. Prepare feature matrix and target vector
    4. Scale numerical features

    Args:
        df: Raw traffic data DataFrame

    Returns:
        tuple: (X, y, encoders, scaler, feature_columns)
    """
    print("Preprocessing data...")

    # Create a copy to avoid modifying original
    df_processed = df.copy()

    # Extract temporal features
    df_processed['hour'] = df_processed['date_time'].dt.hour
    df_processed['day_of_week'] = df_processed['date_time'].dt.dayofweek
    df_processed['is_weekend'] = (df_processed['day_of_week'] >= 5).astype(int)
    df_processed['is_rush_hour'] = (
        ((df_processed['hour'] >= 7) & (df_processed['hour'] <= 9)) |
        ((df_processed['hour'] >= 17) & (df_processed['hour'] <= 19))
    ).astype(int)

    # Initialize label encoders
    le_location = LabelEncoder()
    le_weather = LabelEncoder()
    le_congestion = LabelEncoder()

    # Fit and transform categorical features
    df_processed['location_encoded'] = le_location.fit_transform(df_processed['location'])
    df_processed['weather_encoded'] = le_weather.fit_transform(df_processed['weather'])
    df_processed['congestion_encoded'] = le_congestion.fit_transform(df_processed['congestion_level'])

    # Define feature columns
    feature_columns = [
        'vehicle_count',
        'location_encoded',
        'weather_encoded',
        'hour',
        'day_of_week',
        'is_rush_hour'
    ]

    # Prepare feature matrix (X) and target vector (y)
    X = df_processed[feature_columns].values
    y = df_processed['congestion_encoded'].values

    # Scale numerical features
    scaler = StandardScaler()
    X[:, [0, 3]] = scaler.fit_transform(X[:, [0, 3]])  # Scale vehicle_count and hour

    encoders = {
        'location': le_location,
        'weather': le_weather,
        'congestion': le_congestion
    }

    print(f"Feature matrix shape: {X.shape}")
    print(f"Target vector shape: {y.shape}")
    print(f"Features: {feature_columns}")

    return X, y, encoders, scaler, feature_columns


# ==============================================================================
# MODEL TRAINING
# ==============================================================================

def train_model(X_train, y_train):
    """
    Train a Random Forest Classifier for traffic congestion prediction.

    Random Forest is chosen because:
    - Handles non-linear relationships well
    - Provides feature importance
    - Robust to outliers
    - Works well with categorical features

    Args:
        X_train: Training feature matrix
        y_train: Training target vector

    Returns:
        RandomForestClassifier: Trained model
    """
    print("Training Random Forest Classifier...")

    # Initialize Random Forest Classifier
    # Parameters optimized for traffic prediction
    rf_model = RandomForestClassifier(
        n_estimators=100,          # Number of trees
        max_depth=10,              # Maximum depth of trees
        min_samples_split=5,       # Minimum samples to split a node
        min_samples_leaf=2,        # Minimum samples at leaf node
        random_state=42,           # For reproducibility
        n_jobs=-1,                 # Use all CPU cores
        class_weight='balanced'    # Handle class imbalance
    )

    # Train the model
    rf_model.fit(X_train, y_train)

    print("Model training completed!")
    return rf_model


# ==============================================================================
# MODEL EVALUATION
# ==============================================================================

def evaluate_model(model, X_test, y_test, le_congestion):
    """
    Evaluate the trained model using various metrics.

    Args:
        model: Trained model
        X_test: Test feature matrix
        y_test: Test target vector
        le_congestion: Label encoder for congestion levels

    Returns:
        dict: Evaluation metrics
    """
    print("\n" + "="*50)
    print("MODEL EVALUATION RESULTS")
    print("="*50)

    # Make predictions
    y_pred = model.predict(X_test)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nOverall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

    # Classification report
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=le_congestion.classes_,
        digits=4
    ))

    # Confusion Matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("                  Predicted")
    print("              Low    Medium   High")
    labels = ['Low', 'Medium', 'High']
    for i, label in enumerate(labels):
        print(f"Actual {label:6s}  {cm[i][0]:4d}    {cm[i][1]:4d}   {cm[i][2]:4d}")

    # Feature importance
    print("\nFeature Importance:")
    feature_names = [
        'Vehicle Count',
        'Location',
        'Weather',
        'Hour of Day',
        'Day of Week',
        'Is Rush Hour'
    ]
    importances = model.feature_importances_
    for name, importance in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
        print(f"  {name:15s}: {importance:.4f}")

    return {
        'accuracy': accuracy,
        'confusion_matrix': cm.tolist(),
        'feature_importance': dict(zip(feature_names, importances.tolist()))
    }


# ==============================================================================
# SAVE ARTIFACTS
# ==============================================================================

def save_artifacts(model, encoders, scaler, feature_columns, evaluation_results):
    """
    Save the trained model and preprocessing artifacts.

    Saved files:
    - traffic_model.pkl: Trained Random Forest model
    - le_location.pkl: Label encoder for locations
    - le_weather.pkl: Label encoder for weather
    - le_congestion.pkl: Label encoder for congestion levels
    - scaler.pkl: StandardScaler for numerical features
    - feature_columns.json: List of feature column names
    - model_evaluation.json: Model evaluation metrics

    Args:
        model: Trained model
        encoders: Dictionary of label encoders
        scaler: StandardScaler
        feature_columns: List of feature names
        evaluation_results: Model evaluation metrics
    """
    # Create ml_models directory if it doesn't exist
    ml_models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models')
    os.makedirs(ml_models_dir, exist_ok=True)

    print(f"\nSaving model artifacts to: {ml_models_dir}")

    # Save model
    model_path = os.path.join(ml_models_dir, 'traffic_model.pkl')
    joblib.dump(model, model_path)
    print(f"  ✓ Model saved: traffic_model.pkl")

    # Save encoders
    for name, encoder in encoders.items():
        path = os.path.join(ml_models_dir, f'le_{name}.pkl')
        joblib.dump(encoder, path)
        print(f"  ✓ Encoder saved: le_{name}.pkl")

    # Save scaler
    scaler_path = os.path.join(ml_models_dir, 'scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"  ✓ Scaler saved: scaler.pkl")

    # Save feature columns
    with open(os.path.join(ml_models_dir, 'feature_columns.json'), 'w') as f:
        json.dump(feature_columns, f, indent=2)
    print(f"  ✓ Feature columns saved: feature_columns.json")

    # Save evaluation results
    with open(os.path.join(ml_models_dir, 'model_evaluation.json'), 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    print(f"  ✓ Evaluation results saved: model_evaluation.json")

    print("\nAll artifacts saved successfully!")


# ==============================================================================
# POPULATE DATABASE (OPTIONAL)
# ==============================================================================

def populate_database(df):
    """
    Populate the Django database with synthetic data.

    This is useful for having initial data in the admin panel
    and for the analysis view to work properly.

    Args:
        df: DataFrame with traffic data
    """
    print("\nPopulating database with synthetic data...")

    # Clear existing data
    TrafficData.objects.all().delete()
    print("  ✓ Cleared existing traffic data")

    # Bulk create new records
    traffic_records = []
    for _, row in df.iterrows():
        traffic_records.append(TrafficData(
            date_time=row['date_time'],
            location=row['location'],
            vehicle_count=row['vehicle_count'],
            weather=row['weather'],
            congestion_level=row['congestion_level']
        ))

    TrafficData.objects.bulk_create(traffic_records, batch_size=500)
    print(f"  ✓ Inserted {len(traffic_records)} records into database")


# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

def main():
    """
    Main function to orchestrate the ML training pipeline.

    Pipeline steps:
    1. Generate synthetic traffic data
    2. Preprocess the data
    3. Split into train/test sets
    4. Train the model
    5. Evaluate the model
    6. Save all artifacts
    7. Optionally populate database
    """
    print("="*60)
    print("TRAFFIC CONGESTION PREDICTION - ML TRAINING PIPELINE")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # Step 1: Generate synthetic data
    df = generate_synthetic_data(NUM_RECORDS)

    # Step 2: Preprocess data
    X, y, encoders, scaler, feature_columns = preprocess_data(df)

    # Step 3: Split into train/test sets
    print("\nSplitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Training set size: {X_train.shape[0]}")
    print(f"  Test set size: {X_test.shape[0]}")

    # Step 4: Train model
    model = train_model(X_train, y_train)

    # Step 5: Evaluate model
    evaluation_results = evaluate_model(model, X_test, y_test, encoders['congestion'])

    # Step 6: Save artifacts
    save_artifacts(model, encoders, scaler, feature_columns, evaluation_results)

    # Step 7: Populate database
    populate_database(df)

    # Final summary
    print("\n" + "="*60)
    print("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Start the Django server: python manage.py runserver")
    print("  2. Access the application at: http://127.0.0.1:8000/")
    print("  3. Navigate to /predict/ to test predictions")
    print("  4. Navigate to /analysis/ to view visualizations")
    print("  5. Access admin panel at /admin/ to manage data")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
