"""
AI-Powered Demand Prediction Service for Inventory Management

This module uses machine learning (Linear Regression & Random Forest)
to predict product demand and recommend optimal stock levels.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict

from inventory_system.models import Product, SalesRecord, InventoryPrediction


class DemandPredictor:
    """
    AI-powered demand prediction engine using Machine Learning.

    Features:
    - Linear Regression for trend-based predictions
    - Random Forest for complex patterns
    - Automatic feature engineering (day of week, month, seasonality)
    - Confidence scoring
    - Safety margin calculation
    """

    def __init__(self, safety_margin=0.20, prediction_days=30):
        """
        Initialize the predictor.

        Args:
            safety_margin: Percentage to add as safety buffer (default: 20%)
            prediction_days: Number of days to predict ahead (default: 30)
        """
        self.safety_margin = safety_margin
        self.prediction_days = prediction_days
        self.scaler = StandardScaler()

    def fetch_sales_data(self, product):
        """
        Fetch historical sales data for a product.

        Returns:
            DataFrame with aggregated daily sales
        """
        sales = SalesRecord.objects.filter(product=product).order_by('sale_date')

        if not sales.exists():
            return None

        # Convert to DataFrame
        data = list(sales.values('sale_date', 'quantity_sold'))
        df = pd.DataFrame(data)

        # Aggregate by date (in case there are multiple sales per day)
        df = df.groupby('sale_date').agg({'quantity_sold': 'sum'}).reset_index()
        df['sale_date'] = pd.to_datetime(df['sale_date'])

        # Fill in missing dates with 0 sales
        date_range = pd.date_range(
            start=df['sale_date'].min(),
            end=df['sale_date'].max(),
            freq='D'
        )
        df = df.set_index('sale_date').reindex(date_range, fill_value=0).reset_index()
        df.columns = ['sale_date', 'quantity_sold']

        return df

    def engineer_features(self, df):
        """
        Create features for the ML model.

        Features include:
        - Day of week
        - Month
        - Day of month
        - Week of year
        - Rolling averages (7-day, 30-day)
        - Lag features
        """
        df = df.copy()

        # Time-based features
        df['day_of_week'] = df['sale_date'].dt.dayofweek
        df['month'] = df['sale_date'].dt.month
        df['day_of_month'] = df['sale_date'].dt.day
        df['week_of_year'] = df['sale_date'].dt.isocalendar().week.astype(int)

        # Rolling statistics
        df['rolling_7d'] = df['quantity_sold'].rolling(window=7, min_periods=1).mean()
        df['rolling_30d'] = df['quantity_sold'].rolling(window=30, min_periods=1).mean()

        # Lag features
        df['lag_7'] = df['quantity_sold'].shift(7)
        df['lag_30'] = df['quantity_sold'].shift(30)

        # Fill NaN values
        df['lag_7'].fillna(0, inplace=True)
        df['lag_30'].fillna(0, inplace=True)

        # Create a numeric index for modeling
        df['date_index'] = range(len(df))

        return df

    def train_model(self, df):
        """
        Train ML models and return predictions with confidence scores.

        Uses both Linear Regression and Random Forest,
        then averages their predictions for robustness.
        """
        # Prepare features
        feature_cols = [
            'day_of_week', 'month', 'day_of_month', 'week_of_year',
            'rolling_7d', 'rolling_30d', 'lag_7', 'lag_30', 'date_index'
        ]

        # Ensure all feature columns exist
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            # If we don't have enough data, use simple approach
            return self._simple_prediction(df)

        # Drop rows with NaN values
        df_clean = df.dropna(subset=feature_cols + ['quantity_sold'])

        if len(df_clean) < 30:  # Not enough data for complex modeling
            return self._simple_prediction(df)

        X = df_clean[feature_cols].values
        y = df_clean['quantity_sold'].values

        # Train Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X, y)

        # Train Random Forest
        rf_model = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X, y)

        # Predict for future dates
        future_dates = pd.date_range(
            start=df['sale_date'].max() + timedelta(days=1),
            periods=self.prediction_days,
            freq='D'
        )

        future_df = pd.DataFrame({'sale_date': future_dates})
        future_df['day_of_week'] = future_df['sale_date'].dt.dayofweek
        future_df['month'] = future_df['sale_date'].dt.month
        future_df['day_of_month'] = future_df['sale_date'].dt.day
        future_df['week_of_year'] = future_df['sale_date'].dt.isocalendar().week.astype(int)

        # Use recent averages for rolling and lag features
        recent_avg_7d = df['quantity_sold'].tail(7).mean()
        recent_avg_30d = df['quantity_sold'].tail(30).mean()
        future_df['rolling_7d'] = recent_avg_7d
        future_df['rolling_30d'] = recent_avg_30d
        future_df['lag_7'] = recent_avg_7d
        future_df['lag_30'] = recent_avg_30d

        # Continue date index
        last_index = df['date_index'].max()
        future_df['date_index'] = range(last_index + 1, last_index + 1 + len(future_dates))

        # Make predictions
        X_future = future_df[feature_cols].values
        lr_pred = lr_model.predict(X_future)
        rf_pred = rf_model.predict(X_future)

        # Ensemble: Average predictions
        predictions = (lr_pred + rf_pred) / 2

        # Calculate confidence based on model agreement
        confidence = 1 - np.abs(lr_pred - rf_pred) / (np.abs(predictions) + 1)
        avg_confidence = np.mean(confidence)

        total_demand = int(np.sum(predictions))

        return total_demand, min(max(avg_confidence, 0), 1)

    def _simple_prediction(self, df):
        """
        Fallback simple prediction using recent averages.
        Used when there's not enough data for complex modeling.
        """
        # Use last 30 days average
        recent_avg = df['quantity_sold'].tail(min(30, len(df))).mean()

        # Add small trend based on last 7 days vs previous 7 days
        if len(df) >= 14:
            last_7_avg = df['quantity_sold'].tail(7).mean()
            prev_7_avg = df['quantity_sold'].iloc[-14:-7].mean()
            trend_factor = last_7_avg / (prev_7_avg + 1)
        else:
            trend_factor = 1.0

        daily_prediction = recent_avg * trend_factor
        total_demand = int(daily_prediction * self.prediction_days)

        # Lower confidence for simple model
        confidence = 0.6

        return total_demand, confidence

    def calculate_recommended_stock(self, predicted_demand, current_stock):
        """
        Calculate recommended stock level based on prediction and safety margin.

        Args:
            predicted_demand: AI predicted demand for the period
            current_stock: Current stock level

        Returns:
            Recommended stock level
        """
        # Add safety margin
        recommended = int(predicted_demand * (1 + self.safety_margin))

        # Ensure minimum stock level
        minimum_stock = max(10, int(predicted_demand * 0.3))

        return max(recommended, minimum_stock)

    def predict_for_product(self, product):
        """
        Generate prediction for a single product.

        Returns:
            Dictionary with prediction results
        """
        # Fetch and prepare data
        df = self.fetch_sales_data(product)

        if df is None or len(df) < 7:
            return {
                'product': product,
                'predicted_demand': 0,
                'recommended_stock': 0,
                'status': 'no_data',
                'confidence': 0
            }

        # Engineer features and train model
        result = self.train_model(df)

        if isinstance(result, tuple):
            predicted_demand, confidence = result
        else:
            predicted_demand = result
            confidence = 0.5

        # Calculate recommended stock
        recommended_stock = self.calculate_recommended_stock(
            predicted_demand,
            product.current_stock
        )

        # Determine status
        if product.current_stock < recommended_stock:
            status = 'low_stock'
        elif product.current_stock > recommended_stock * 1.5:
            status = 'overstock'
        else:
            status = 'optimal'

        return {
            'product': product,
            'predicted_demand': predicted_demand,
            'recommended_stock': recommended_stock,
            'status': status,
            'confidence': round(confidence, 3)
        }

    def predict_all_products(self):
        """
        Generate predictions for all products in the database.

        Returns:
            List of prediction dictionaries
        """
        products = Product.objects.all()
        predictions = []

        for product in products:
            prediction = self.predict_for_product(product)
            predictions.append(prediction)

        return predictions

    def save_predictions(self):
        """
        Generate and save predictions to the database.
        This creates new InventoryPrediction records.
        """
        predictions = self.predict_all_products()

        created_count = 0
        for pred in predictions:
            if pred['status'] != 'no_data':
                InventoryPrediction.objects.create(
                    product=pred['product'],
                    predicted_demand=pred['predicted_demand'],
                    recommended_stock=pred['recommended_stock'],
                    status=pred['status'],
                    confidence_score=pred['confidence']
                )
                created_count += 1

        return created_count

    def get_historical_for_chart(self, product):
        """
        Get historical and predicted data for Chart.js visualization.

        Returns:
            Dictionary with labels and datasets for the chart
        """
        df = self.fetch_sales_data(product)

        if df is None:
            return {
                'labels': [],
                'historical': [],
                'predicted': []
            }

        # Get historical data (last 90 days)
        historical_df = df.tail(90)
        labels = historical_df['sale_date'].dt.strftime('%Y-%m-%d').tolist()
        historical = historical_df['quantity_sold'].tolist()

        # Generate prediction dates
        last_date = df['sale_date'].max()
        pred_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=min(30, self.prediction_days),
            freq='D'
        )
        pred_labels = pred_dates.strftime('%Y-%m-%d').tolist()

        # Get prediction
        prediction = self.predict_for_product(product)
        daily_prediction = prediction['predicted_demand'] / self.prediction_days
        predicted = [int(daily_prediction)] * len(pred_labels)

        # Combine
        all_labels = labels + pred_labels
        all_historical = historical + [None] * len(pred_labels)
        all_predicted = [None] * len(labels) + predicted

        return {
            'labels': all_labels,
            'historical': all_historical,
            'predicted': all_predicted
        }


def run_predictions():
    """
    Convenience function to run predictions and save to database.
    Can be called from management commands or views.
    """
    predictor = DemandPredictor()
    return predictor.save_predictions()
