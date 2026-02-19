"""
AI-Driven Fleet Management Utilities

This module contains AI/ML logic for:
1. Predictive maintenance using Linear Regression
2. Usage analysis with pandas
3. Cost optimization calculations
4. Alert generation based on predictions
"""

import pandas as pd
import numpy as np
from django.db.models import Sum, Avg, Count, Q, F, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

from .models import Vehicle, Trip, MaintenanceRecord, Alert


class FleetAnalytics:
    """
    Core analytics class for fleet management using pandas
    """

    @staticmethod
    def get_trip_dataframe(vehicle_id: Optional[int] = None) -> pd.DataFrame:
        """
        Fetch trip data and return as pandas DataFrame for analysis

        Args:
            vehicle_id: Optional vehicle ID to filter trips

        Returns:
            pandas DataFrame with trip data
        """
        queryset = Trip.objects.select_related('vehicle', 'driver').all()

        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)

        # Convert queryset to DataFrame
        data = list(queryset.values(
            'id', 'vehicle__plate', 'vehicle__id', 'driver__name',
            'start_date', 'end_date', 'distance', 'fuel_used',
            'status', 'start_location', 'end_location'
        ))

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])

        # Calculate derived metrics
        df['fuel_efficiency'] = df.apply(
            lambda row: row['distance'] / row['fuel_used'] if row['fuel_used'] > 0 else 0,
            axis=1
        )
        df['duration_hours'] = df.apply(
            lambda row: (row['end_date'] - row['start_date']).total_seconds() / 3600
            if pd.notna(row['end_date']) else 0,
            axis=1
        )

        return df

    @staticmethod
    def get_maintenance_dataframe(vehicle_id: Optional[int] = None) -> pd.DataFrame:
        """
        Fetch maintenance data and return as pandas DataFrame

        Args:
            vehicle_id: Optional vehicle ID to filter maintenance records

        Returns:
            pandas DataFrame with maintenance data
        """
        queryset = MaintenanceRecord.objects.select_related('vehicle').all()

        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)

        data = list(queryset.values(
            'id', 'vehicle__plate', 'vehicle__id', 'vehicle__current_mileage',
            'date', 'maintenance_type', 'mileage_at_service',
            'cost', 'severity', 'description'
        ))

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])

        return df

    @staticmethod
    def calculate_usage_stats(vehicle_id: Optional[int] = None) -> Dict:
        """
        Calculate comprehensive usage statistics using pandas

        Args:
            vehicle_id: Optional vehicle ID to filter

        Returns:
            Dictionary with usage statistics
        """
        df = FleetAnalytics.get_trip_dataframe(vehicle_id)

        if df.empty:
            return {
                'total_trips': 0,
                'total_distance': 0,
                'total_fuel_used': 0,
                'average_fuel_efficiency': 0,
                'average_trip_distance': 0,
                'total_duration_hours': 0
            }

        stats = {
            'total_trips': len(df),
            'total_distance': float(df['distance'].sum()),
            'total_fuel_used': float(df['fuel_used'].sum()),
            'average_fuel_efficiency': float(df['fuel_efficiency'].mean()) if df['fuel_efficiency'].mean() > 0 else 0,
            'average_trip_distance': float(df['distance'].mean()),
            'total_duration_hours': float(df['duration_hours'].sum())
        }

        return stats

    @staticmethod
    def get_monthly_costs(vehicle_id: Optional[int] = None) -> pd.DataFrame:
        """
        Calculate monthly costs per vehicle using pandas

        Args:
            vehicle_id: Optional vehicle ID to filter

        Returns:
            DataFrame with monthly cost breakdown
        """
        maint_df = FleetAnalytics.get_maintenance_dataframe(vehicle_id)

        if maint_df.empty:
            return pd.DataFrame()

        # Group by vehicle and month
        maint_df['year_month'] = maint_df['date'].dt.to_period('M')
        monthly_costs = maint_df.groupby(['vehicle__plate', 'year_month']).agg({
            'cost': 'sum'
        }).reset_index()
        monthly_costs['year_month'] = monthly_costs['year_month'].astype(str)

        return monthly_costs

    @staticmethod
    def get_fuel_efficiency_trends(vehicle_id: Optional[int] = None) -> pd.DataFrame:
        """
        Analyze fuel efficiency trends over time

        Args:
            vehicle_id: Optional vehicle ID to filter

        Returns:
            DataFrame with fuel efficiency trends
        """
        df = FleetAnalytics.get_trip_dataframe(vehicle_id)

        if df.empty:
            return pd.DataFrame()

        # Group by vehicle and month
        df['year_month'] = df['start_date'].dt.to_period('M')
        trends = df.groupby(['vehicle__plate', 'year_month']).agg({
            'distance': 'sum',
            'fuel_used': 'sum',
            'fuel_efficiency': 'mean'
        }).reset_index()
        trends['year_month'] = trends['year_month'].astype(str)

        return trends


class PredictiveMaintenanceAI:
    """
    AI-based predictive maintenance using scikit-learn Linear Regression
    """

    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()

    def predict_next_maintenance_mileage(self, vehicle: Vehicle) -> Dict:
        """
        Predict when the next maintenance should occur based on historical data

        Uses Linear Regression to analyze:
        - Past maintenance intervals
        - Mileage accumulation patterns
        - Cost patterns

        Args:
            vehicle: Vehicle instance

        Returns:
            Dictionary with prediction results
        """
        # Get maintenance history for this vehicle
        maintenance_records = MaintenanceRecord.objects.filter(
            vehicle=vehicle
        ).order_by('date')

        if maintenance_records.count() < 2:
            # Not enough data for prediction - use rule-based approach
            return self._rule_based_prediction(vehicle)

        # Prepare data for ML model
        data = []
        target = []

        records = list(maintenance_records)
        for i in range(1, len(records)):
            prev_mileage = float(records[i - 1].mileage_at_service)
            curr_mileage = float(records[i].mileage_at_service)
            interval = curr_mileage - prev_mileage
            cost = float(records[i].cost)
            days_since_prev = (records[i].date - records[i - 1].date).days

            # Features: previous interval, cost, days since last maintenance
            data.append([interval, cost, days_since_prev])
            target.append(interval)

        if len(data) < 2:
            return self._rule_based_prediction(vehicle)

        # Prepare features and target
        X = np.array(data)
        y = np.array(target)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled, y)

        # Predict next interval
        current_mileage = float(vehicle.current_mileage)
        last_maintenance = maintenance_records.last()
        last_mileage = float(last_maintenance.mileage_at_service)

        # Feature vector for prediction
        last_interval = last_mileage - float(maintenance_records[maintenance_records.count() - 2].mileage_at_service)
        last_cost = float(last_maintenance.cost)
        days_since_last = (datetime.now().date() - last_maintenance.date.date()).days

        # Predict next maintenance mileage
        X_pred = self.scaler.transform([[last_interval, last_cost, days_since_last]])
        predicted_interval = self.model.predict(X_pred)[0]

        # Calculate predicted next maintenance mileage
        predicted_mileage = last_mileage + max(predicted_interval, 1000)  # At least 1000 miles
        miles_until_maintenance = max(0, predicted_mileage - current_mileage)

        # Calculate confidence based on model score
        confidence = max(0.5, min(0.95, self.model.score(X_scaled, y)))

        # Determine urgency
        urgency = self._determine_urgency(miles_until_maintenance, confidence)

        return {
            'vehicle_id': vehicle.id,
            'vehicle_plate': vehicle.plate,
            'current_mileage': current_mileage,
            'last_maintenance_mileage': last_mileage,
            'last_maintenance_date': last_maintenance.date.date(),
            'predicted_next_maintenance_mileage': round(predicted_mileage, 2),
            'miles_until_maintenance': round(miles_until_maintenance, 2),
            'predicted_interval': round(predicted_interval, 2),
            'confidence': round(confidence, 2),
            'urgency': urgency,
            'prediction_method': 'linear_regression'
        }

    def _rule_based_prediction(self, vehicle: Vehicle) -> Dict:
        """
        Fallback rule-based prediction when insufficient ML data

        Args:
            vehicle: Vehicle instance

        Returns:
            Dictionary with rule-based prediction
        """
        current_mileage = float(vehicle.current_mileage)

        last_maintenance = MaintenanceRecord.objects.filter(
            vehicle=vehicle
        ).order_by('-date').first()

        if last_maintenance:
            last_mileage = float(last_maintenance.mileage_at_service)
            last_date = last_maintenance.date.date()
        else:
            last_mileage = 0
            last_date = vehicle.purchase_date

        # Standard intervals by vehicle type
        standard_intervals = {
            'truck': 10000,
            'van': 7500,
            'sedan': 5000,
            'suv': 7500,
            'motorcycle': 3000,
            'bus': 12000,
            'other': 5000
        }

        interval = standard_intervals.get(vehicle.vehicle_type, 5000)
        predicted_mileage = last_mileage + interval
        miles_until_maintenance = max(0, predicted_mileage - current_mileage)

        urgency = self._determine_urgency(miles_until_maintenance, 0.7)

        return {
            'vehicle_id': vehicle.id,
            'vehicle_plate': vehicle.plate,
            'current_mileage': current_mileage,
            'last_maintenance_mileage': last_mileage,
            'last_maintenance_date': last_date,
            'predicted_next_maintenance_mileage': round(predicted_mileage, 2),
            'miles_until_maintenance': round(miles_until_maintenance, 2),
            'predicted_interval': interval,
            'confidence': 0.70,
            'urgency': urgency,
            'prediction_method': 'rule_based'
        }

    def _determine_urgency(self, miles_until: float, confidence: float) -> str:
        """
        Determine urgency level based on miles until maintenance

        Args:
            miles_until: Miles until next maintenance
            confidence: Model confidence score

        Returns:
            Urgency level string
        """
        if miles_until <= 500:
            return 'critical'
        elif miles_until <= 1000:
            return 'high'
        elif miles_until <= 2000:
            return 'medium'
        else:
            return 'low'

    def predict_failure_probability(self, vehicle: Vehicle) -> Dict:
        """
        Predict potential failure probability based on multiple factors

        Args:
            vehicle: Vehicle instance

        Returns:
            Dictionary with failure probability assessment
        """
        current_mileage = float(vehicle.current_mileage)

        # Get maintenance history
        maintenance_records = MaintenanceRecord.objects.filter(vehicle=vehicle)
        total_maintenance_cost = float(maintenance_records.aggregate(Sum('cost'))['cost__sum'] or 0)

        # Get recent trips
        recent_trips = Trip.objects.filter(
            vehicle=vehicle,
            status='completed'
        ).order_by('-start_date')[:20]

        if not recent_trips:
            recent_efficiency = 0
        else:
            recent_efficiency = sum(t.fuel_efficiency for t in recent_trips) / len(recent_trips)

        # Risk factors
        risk_factors = []

        # High mileage risk
        if current_mileage > 100000:
            risk_factors.append(('high_mileage', min(1.0, current_mileage / 200000)))

        # Low efficiency risk
        if recent_efficiency > 0 and recent_efficiency < 15:
            risk_factors.append(('low_efficiency', 1 - (recent_efficiency / 15)))

        # High maintenance cost (frequent repairs)
        if maintenance_records.count() > 5:
            avg_cost = total_maintenance_cost / maintenance_records.count()
            if avg_cost > 500:
                risk_factors.append(('high_maintenance', min(1.0, avg_cost / 1000)))

        # Overdue maintenance
        last_maintenance = maintenance_records.order_by('-date').first()
        if last_maintenance:
            days_since = (datetime.now().date() - last_maintenance.date.date()).days
            if days_since > 90:
                risk_factors.append(('overdue_maintenance', min(1.0, days_since / 180)))

        # Calculate overall probability
        if risk_factors:
            total_risk = sum(r[1] for r in risk_factors) / len(risk_factors)
            failure_probability = min(0.95, total_risk)
        else:
            failure_probability = 0.1

        # Determine risk level
        if failure_probability > 0.7:
            risk_level = 'critical'
        elif failure_probability > 0.5:
            risk_level = 'high'
        elif failure_probability > 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'vehicle_id': vehicle.id,
            'vehicle_plate': vehicle.plate,
            'failure_probability': round(failure_probability, 2),
            'risk_level': risk_level,
            'risk_factors': [{'factor': r[0], 'score': round(r[1], 2)} for r in risk_factors],
            'recommendation': self._get_recommendation(risk_level)
        }

    def _get_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            'critical': 'Immediate inspection required. Vehicle should be taken out of service.',
            'high': 'Schedule maintenance within 1 week. Monitor vehicle closely.',
            'medium': 'Schedule maintenance within 2-3 weeks. Continue monitoring.',
            'low': 'Continue normal operation. Schedule routine maintenance as planned.'
        }
        return recommendations.get(risk_level, 'Continue normal operation.')


class AlertGenerator:
    """
    Generate predictive alerts based on AI analysis
    """

    @staticmethod
    def generate_maintenance_alerts() -> int:
        """
        Generate maintenance alerts for all vehicles based on predictions

        Returns:
            Number of alerts created
        """
        ai = PredictiveMaintenanceAI()
        alerts_created = 0

        for vehicle in Vehicle.objects.filter(status='active'):
            # Get predictions
            prediction = ai.predict_next_maintenance_mileage(vehicle)
            failure_prediction = ai.predict_failure_probability(vehicle)

            # Check if maintenance alert needed
            miles_until = prediction['miles_until_maintenance']

            if miles_until <= 500:
                alert_type = 'maintenance_overdue'
                severity = 'critical'
            elif miles_until <= 1000:
                alert_type = 'maintenance_due'
                severity = 'warning'
            elif miles_until <= 2000:
                alert_type = 'maintenance_due'
                severity = 'info'
            else:
                alert_type = None

            # Create maintenance alert if needed
            if alert_type:
                message = (
                    f"{prediction['vehicle_plate']} requires maintenance. "
                    f"Predicted maintenance in {round(miles_until)} miles "
                    f"(at {round(prediction['predicted_next_maintenance_mileage'])} miles). "
                    f"Confidence: {prediction['confidence'] * 100}%."
                )

                # Check if similar alert already exists
                existing_alert = Alert.objects.filter(
                    vehicle=vehicle,
                    alert_type=alert_type,
                    is_active=True
                ).first()

                if not existing_alert:
                    Alert.objects.create(
                        vehicle=vehicle,
                        alert_type=alert_type,
                        message=message,
                        severity=severity
                    )
                    alerts_created += 1

            # Check if low efficiency alert needed
            if failure_prediction['risk_factors']:
                for factor in failure_prediction['risk_factors']:
                    if factor['factor'] == 'low_efficiency' and factor['score'] > 0.3:
                        message = (
                            f"{vehicle.plate} shows low fuel efficiency. "
                            f"This may indicate engine issues requiring attention."
                        )

                        existing_alert = Alert.objects.filter(
                            vehicle=vehicle,
                            alert_type='low_efficiency',
                            is_active=True
                        ).first()

                        if not existing_alert:
                            severity = 'warning' if factor['score'] > 0.5 else 'info'
                            Alert.objects.create(
                                vehicle=vehicle,
                                alert_type='low_efficiency',
                                message=message,
                                severity=severity
                            )
                            alerts_created += 1

            # High failure probability alert
            if failure_prediction['failure_probability'] > 0.6:
                message = (
                    f"{vehicle.plate} has high failure probability "
                    f"({round(failure_prediction['failure_probability'] * 100)}%). "
                    f"Recommendation: {failure_prediction['recommendation']}"
                )

                existing_alert = Alert.objects.filter(
                    vehicle=vehicle,
                    alert_type='safety',
                    is_active=True
                ).first()

                if not existing_alert:
                    severity = 'critical' if failure_prediction['failure_probability'] > 0.7 else 'warning'
                    Alert.objects.create(
                        vehicle=vehicle,
                        alert_type='safety',
                        message=message,
                        severity=severity
                    )
                    alerts_created += 1

        return alerts_created


class CostOptimizer:
    """
    Calculate cost optimization metrics
    """

    @staticmethod
    def calculate_efficiency_ratings() -> List[Dict]:
        """
        Calculate efficiency ratings for all vehicles

        Returns:
            List of vehicles with efficiency metrics
        """
        vehicles_data = []

        for vehicle in Vehicle.objects.all():
            # Get trip statistics
            trips = Trip.objects.filter(vehicle=vehicle, status='completed')
            total_distance = float(vehicle.total_distance)
            total_fuel = float(vehicle.total_fuel_used)
            total_maintenance = float(vehicle.total_maintenance_cost)

            if total_distance == 0:
                continue

            # Calculate metrics
            fuel_efficiency = vehicle.fuel_efficiency
            cost_per_mile = vehicle.cost_per_mile
            utilization = trips.count() if trips.count() > 0 else 0

            # Calculate efficiency rating (0-100)
            # Base rating on fuel efficiency and cost per mile
            if fuel_efficiency > 0:
                efficiency_score = min(100, (fuel_efficiency / 30) * 50)  # Up to 50 points for efficiency
                cost_score = max(0, 50 - (cost_per_mile * 2))  # Up to 50 points for low cost
                rating = round(efficiency_score + cost_score)
            else:
                rating = 0

            vehicles_data.append({
                'vehicle_id': vehicle.id,
                'plate': vehicle.plate,
                'make_model': f"{vehicle.make} {vehicle.model}",
                'fuel_efficiency': fuel_efficiency,
                'cost_per_mile': cost_per_mile,
                'total_distance': total_distance,
                'total_maintenance_cost': total_maintenance,
                'utilization_days': utilization,
                'rating': rating,
                'rating_label': CostOptimizer._get_rating_label(rating)
            })

        # Sort by rating descending
        vehicles_data.sort(key=lambda x: x['rating'], reverse=True)

        return vehicles_data

    @staticmethod
    def _get_rating_label(rating: int) -> str:
        """Get rating label based on score"""
        if rating >= 80:
            return 'Excellent'
        elif rating >= 60:
            return 'Good'
        elif rating >= 40:
            return 'Fair'
        else:
            return 'Poor'
