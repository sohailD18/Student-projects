"""
AI/ML Forecasting Utilities for Demand Prediction

This module contains the core forecasting logic:
- Data preprocessing and aggregation
- Feature engineering
- Model training (Linear Regression)
- Forecast generation
- Replenishment suggestions
"""

from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')


# Forecasting Configuration
FORECAST_DAYS = 30  # Number of days to forecast
MIN_DATA_POINTS = 10  # Minimum historical data points required
SAFETY_STOCK_MULTIPLIER = 1.5  # Safety stock multiplier


def get_historical_sales_data(product_id):
    """
    Fetch and aggregate historical sales data for a product.

    Args:
        product_id: ID of the product

    Returns:
        DataFrame: Aggregated sales data with date and quantity
    """
    from .models import SalesData

    # Fetch sales data from database
    sales_data = SalesData.objects.filter(
        product_id=product_id
    ).values('date').annotate(
        total_quantity=Sum('quantity_sold')
    ).order_by('date')

    # Convert to DataFrame
    if not sales_data:
        return None

    df = pd.DataFrame(list(sales_data))

    # Ensure date is datetime type
    df['date'] = pd.to_datetime(df['date'])

    return df


def prepare_features(df):
    """
    Engineer features for machine learning model.

    Features created:
    - days_since_start: Linear trend
    - day_of_week: Weekly seasonality
    - day_of_month: Monthly seasonality
    - month: Yearly seasonality
    - quarter: Quarterly seasonality

    Args:
        df: DataFrame with 'date' column

    Returns:
        DataFrame: Original df with added features
    """
    df = df.copy()

    # Calculate days since start (for trend)
    df['days_since_start'] = (df['date'] - df['date'].min()).dt.days

    # Temporal features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter

    # Lag features (previous day sales)
    df['lag_1'] = df['total_quantity'].shift(1)
    df['lag_7'] = df['total_quantity'].shift(7)

    # Rolling average features
    df['rolling_mean_7'] = df['total_quantity'].rolling(window=7, min_periods=1).mean()
    df['rolling_mean_30'] = df['total_quantity'].rolling(window=30, min_periods=1).mean()

    return df


def train_forecasting_model(df):
    """
    Train a Linear Regression model for demand forecasting.

    The model uses multiple features:
    - Trend (days_since_start)
    - Seasonality (day_of_week, month)
    - Lag features (previous sales)
    - Rolling averages

    Args:
        df: DataFrame with prepared features

    Returns:
        tuple: (model, scaler, feature_columns, last_date)
    """
    # Prepare features
    df_featured = prepare_features(df)

    # Drop NaN values created by lag features
    df_featured = df_featured.dropna()

    if len(df_featured) < MIN_DATA_POINTS:
        return None, None, None, None

    # Select features for model
    feature_columns = [
        'days_since_start',
        'day_of_week',
        'day_of_month',
        'month',
        'rolling_mean_7',
        'rolling_mean_30'
    ]

    # Remove features that might not exist for small datasets
    available_features = [col for col in feature_columns if col in df_featured.columns]

    X = df_featured[available_features].values
    y = df_featured['total_quantity'].values

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train model
    model = LinearRegression()
    model.fit(X_scaled, y)

    return model, scaler, available_features, df_featured['date'].max()


def generate_forecast(product_id, days=FORECAST_DAYS):
    """
    Generate demand forecast for a product.

    This function:
    1. Fetches historical sales data
    2. Trains a forecasting model
    3. Predicts future demand
    4. Calculates confidence intervals

    Args:
        product_id: ID of the product
        days: Number of days to forecast (default: 30)

    Returns:
        dict: Forecast results with predictions and metadata
    """
    from .models import Product, SalesData

    # Get product info
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return {
            'error': 'Product not found',
            'product_id': product_id
        }

    # Get historical data
    df = get_historical_sales_data(product_id)

    if df is None or len(df) < MIN_DATA_POINTS:
        # Fallback to simple average if insufficient data
        return generate_simple_forecast(product_id, days)

    # Train model
    model, scaler, feature_columns, last_date = train_forecasting_model(df)

    if model is None:
        return generate_simple_forecast(product_id, days)

    # Generate future dates
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=days,
        freq='D'
    )

    # Prepare features for prediction
    future_df = pd.DataFrame({'date': future_dates})
    future_df['days_since_start'] = (future_df['date'] - df['date'].min()).dt.days
    future_df['day_of_week'] = future_df['date'].dt.dayofweek
    future_df['day_of_month'] = future_df['date'].dt.day
    future_df['month'] = future_df['date'].dt.month

    # Calculate rolling averages using historical data
    recent_avg_7 = df.tail(7)['total_quantity'].mean()
    recent_avg_30 = df.tail(min(30, len(df)))['total_quantity'].mean()
    future_df['rolling_mean_7'] = recent_avg_7
    future_df['rolling_mean_30'] = recent_avg_30

    # Ensure only available features are used
    available_features = [col for col in feature_columns if col in future_df.columns]
    X_future = future_df[available_features].values

    # Scale features
    X_future_scaled = scaler.transform(X_future)

    # Make predictions
    predictions = model.predict(X_future_scaled)

    # Ensure predictions are non-negative
    predictions = np.maximum(predictions, 0)

    # Calculate statistics
    total_predicted_demand = int(round(predictions.sum()))
    average_daily_demand = float(round(predictions.mean(), 2))
    max_daily_demand = int(round(predictions.max()))
    min_daily_demand = int(round(predictions.min()))

    # Calculate replenishment suggestion
    suggested_order_quantity = max(
        0,
        total_predicted_demand + product.safety_stock - product.current_stock
    )

    # Determine status
    if product.current_stock == 0:
        status = 'out_of_stock'
        status_display = 'Out of Stock'
    elif product.current_stock < product.safety_stock:
        status = 'critical'
        status_display = 'Critical'
    elif product.current_stock < total_predicted_demand + product.safety_stock:
        status = 'low'
        status_display = 'Low Stock'
    elif product.current_stock > total_predicted_demand * 2:
        status = 'overstock'
        status_display = 'Over-stock'
    else:
        status = 'good'
        status_display = 'Good'

    # Prepare daily forecast data
    daily_forecast = [
        {
            'date': date.strftime('%Y-%m-%d'),
            'predicted_quantity': int(round(pred))
        }
        for date, pred in zip(future_dates, predictions)
    ]

    return {
        'product_id': product_id,
        'product_name': product.name,
        'current_stock': product.current_stock,
        'safety_stock': product.safety_stock,
        'total_predicted_demand': total_predicted_demand,
        'average_daily_demand': average_daily_demand,
        'max_daily_demand': max_daily_demand,
        'min_daily_demand': min_daily_demand,
        'suggested_order_quantity': suggested_order_quantity,
        'status': status,
        'status_display': status_display,
        'forecast_days': days,
        'daily_forecast': daily_forecast,
        'historical_data_points': len(df),
        'model_used': 'Linear Regression'
    }


def generate_simple_forecast(product_id, days=FORECAST_DAYS):
    """
    Generate a simple forecast using moving average when insufficient data for ML model.

    Args:
        product_id: ID of the product
        days: Number of days to forecast

    Returns:
        dict: Simple forecast results
    """
    from .models import Product, SalesData

    product = Product.objects.get(id=product_id)

    # Get historical data
    sales_data = SalesData.objects.filter(product_id=product_id)
    total_sales = sales_data.aggregate(total=Sum('quantity_sold'))['total'] or 0
    days_with_sales = sales_data.values('date').distinct().count()

    if days_with_sales == 0:
        days_with_sales = 1

    # Calculate average daily sales
    avg_daily_sales = total_sales / days_with_sales

    # Generate forecast
    daily_forecast = []
    for i in range(days):
        future_date = datetime.now().date() + timedelta(days=i+1)
        daily_forecast.append({
            'date': future_date.strftime('%Y-%m-%d'),
            'predicted_quantity': int(round(avg_daily_sales))
        })

    total_predicted_demand = int(round(avg_daily_sales * days))
    suggested_order_quantity = max(
        0,
        total_predicted_demand + product.safety_stock - product.current_stock
    )

    # Determine status
    if product.current_stock == 0:
        status = 'out_of_stock'
        status_display = 'Out of Stock'
    elif product.current_stock < product.safety_stock:
        status = 'critical'
        status_display = 'Critical'
    elif product.current_stock < total_predicted_demand + product.safety_stock:
        status = 'low'
        status_display = 'Low Stock'
    elif product.current_stock > total_predicted_demand * 2:
        status = 'overstock'
        status_display = 'Over-stock'
    else:
        status = 'good'
        status_display = 'Good'

    return {
        'product_id': product_id,
        'product_name': product.name,
        'current_stock': product.current_stock,
        'safety_stock': product.safety_stock,
        'total_predicted_demand': total_predicted_demand,
        'average_daily_demand': round(avg_daily_sales, 2),
        'max_daily_demand': int(round(avg_daily_sales)),
        'min_daily_demand': int(round(avg_daily_sales)),
        'suggested_order_quantity': suggested_order_quantity,
        'status': status,
        'status_display': status_display,
        'forecast_days': days,
        'daily_forecast': daily_forecast,
        'historical_data_points': days_with_sales,
        'model_used': 'Moving Average'
    }


def get_all_products_forecast():
    """
    Generate forecasts for all products in the system.

    Returns:
        list: List of forecast dictionaries for all products
    """
    from .models import Product

    products = Product.objects.all()
    forecasts = []

    for product in products:
        forecast = generate_forecast(product.id)
        forecasts.append(forecast)

    return forecasts


def get_dashboard_stats():
    """
    Calculate aggregate statistics for the dashboard.

    Returns:
        dict: Dashboard statistics including KPIs
    """
    from .models import Product, SalesData

    # Total products
    total_products = Product.objects.count()

    # Total inventory value
    products = Product.objects.all()
    total_inventory_value = sum(p.inventory_value for p in products)

    # Low stock alerts
    forecasts = get_all_products_forecast()
    low_stock_count = sum(
        1 for f in forecasts
        if f.get('status') in ['low', 'critical', 'out_of_stock']
    )

    # Recent sales (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_sales = SalesData.objects.filter(date__gte=thirty_days_ago)
    total_recent_sales = recent_sales.aggregate(
        total=Sum('quantity_sold')
    )['total'] or 0

    average_daily_sales = total_recent_sales / 30 if total_recent_sales > 0 else 0

    # Category breakdown
    category_counts = {}
    for product in products:
        category = product.get_category_display()
        category_counts[category] = category_counts.get(category, 0) + 1

    return {
        'total_products': total_products,
        'total_inventory_value': float(total_inventory_value),
        'low_stock_count': low_stock_count,
        'total_recent_sales': total_recent_sales,
        'average_daily_sales': round(average_daily_sales, 2),
        'category_counts': category_counts
    }


def get_historical_sales_for_chart(product_id, days=90):
    """
    Get historical sales data formatted for Chart.js.

    Args:
        product_id: ID of the product
        days: Number of days of historical data to include

    Returns:
        dict: Sales data with labels and values
    """
    from .models import SalesData

    start_date = datetime.now().date() - timedelta(days=days)

    sales_data = SalesData.objects.filter(
        product_id=product_id,
        date__gte=start_date
    ).values('date').annotate(
        total_quantity=Sum('quantity_sold')
    ).order_by('date')

    labels = [item['date'].strftime('%Y-%m-%d') for item in sales_data]
    values = [item['total_quantity'] for item in sales_data]

    return {
        'labels': labels,
        'values': values
    }


def calculate_trend_analysis(product_id, days=90):
    """
    Perform detailed trend analysis on product sales.

    Calculates:
    - Growth rate (percentage)
    - Trend direction (increasing/decreasing/stable)
    - Volatility measure
    - Seasonal patterns
    - Moving averages

    Args:
        product_id: ID of the product
        days: Number of days to analyze

    Returns:
        dict: Trend analysis results
    """
    df = get_historical_sales_data(product_id)

    if df is None or len(df) < 5:
        return {
            'error': 'Insufficient data for trend analysis',
            'product_id': product_id
        }

    # Filter to requested period
    cutoff_date = datetime.now().date() - timedelta(days=days)
    df = df[df['date'] >= pd.Timestamp(cutoff_date)]

    # Calculate moving averages
    df['ma_7'] = df['total_quantity'].rolling(window=7, min_periods=1).mean()
    df['ma_30'] = df['total_quantity'].rolling(window=min(30, len(df)), min_periods=1).mean()

    # Calculate growth rate (comparing first half to second half)
    mid_point = len(df) // 2
    first_half_avg = df['total_quantity'][:mid_point].mean()
    second_half_avg = df['total_quantity'][mid_point:].mean()

    if first_half_avg > 0:
        growth_rate = ((second_half_avg - first_half_avg) / first_half_avg) * 100
    else:
        growth_rate = 0

    # Determine trend direction
    if growth_rate > 5:
        trend_direction = 'increasing'
        trend_display = 'Rising Trend'
    elif growth_rate < -5:
        trend_direction = 'decreasing'
        trend_display = 'Falling Trend'
    else:
        trend_direction = 'stable'
        trend_display = 'Stable'

    # Calculate volatility (standard deviation / mean)
    volatility = (df['total_quantity'].std() / df['total_quantity'].mean()) * 100 if df['total_quantity'].mean() > 0 else 0

    # Detect seasonal pattern (day of week analysis)
    df['day_of_week'] = df['date'].dt.dayofweek
    dow_avg = df.groupby('day_of_week')['total_quantity'].mean()
    peak_day = dow_avg.idxmax()
    peak_day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Calculate momentum (recent vs overall average)
    recent_7_days = df.tail(7)['total_quantity'].mean()
    overall_avg = df['total_quantity'].mean()
    if overall_avg > 0:
        momentum = ((recent_7_days - overall_avg) / overall_avg) * 100
    else:
        momentum = 0

    return {
        'product_id': product_id,
        'analysis_period_days': len(df),
        'growth_rate': round(growth_rate, 2),
        'trend_direction': trend_direction,
        'trend_display': trend_display,
        'volatility': round(volatility, 2),
        'momentum': round(momentum, 2),
        'peak_sales_day': peak_day_names[peak_day],
        'current_7day_avg': round(df['ma_7'].iloc[-1], 2),
        'current_30day_avg': round(df['ma_30'].iloc[-1], 2),
        'overall_average': round(overall_avg, 2),
        'max_sales': int(df['total_quantity'].max()),
        'min_sales': int(df['total_quantity'].min()),
        'total_sales_in_period': int(df['total_quantity'].sum())
    }


def calculate_model_accuracy(product_id):
    """
    Calculate model accuracy metrics using backtesting.

    Performs walk-forward validation to estimate forecast accuracy.

    Metrics calculated:
    - MAPE (Mean Absolute Percentage Error)
    - RMSE (Root Mean Square Error)
    - MAE (Mean Absolute Error)
    - R-squared score

    Args:
        product_id: ID of the product

    Returns:
        dict: Model accuracy metrics
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    df = get_historical_sales_data(product_id)

    if df is None or len(df) < 20:
        return {
            'error': 'Insufficient data for accuracy calculation (need 20+ days)',
            'product_id': product_id
        }

    # Use last 20% for testing
    split_point = int(len(df) * 0.8)
    train_df = df[:split_point].copy()
    test_df = df[split_point:].copy()

    if len(test_df) < 5:
        return {
            'error': 'Insufficient test data',
            'product_id': product_id
        }

    # Prepare features for training
    train_df_featured = prepare_features(train_df)
    train_df_featured = train_df_featured.dropna()

    if len(train_df_featured) < MIN_DATA_POINTS:
        return {
            'error': 'Insufficient training data after feature preparation',
            'product_id': product_id
        }

    # Train model
    model, scaler, feature_columns, _ = train_forecasting_model(train_df)

    if model is None:
        return {
            'error': 'Could not train model',
            'product_id': product_id
        }

    # Prepare test features
    test_df_featured = prepare_features(test_df)
    test_df_featured = test_df_featured.dropna()

    available_features = [col for col in feature_columns if col in test_df_featured.columns]
    X_test = test_df_featured[available_features].values
    y_test = test_df_featured['total_quantity'].values

    # Scale and predict
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    y_pred = np.maximum(y_pred, 0)  # Ensure non-negative

    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # MAPE calculation (avoid division by zero)
    non_zero_mask = y_test > 0
    if non_zero_mask.sum() > 0:
        mape = np.mean(np.abs((y_test[non_zero_mask] - y_pred[non_zero_mask]) / y_test[non_zero_mask])) * 100
    else:
        mape = 0

    # R-squared
    r2 = r2_score(y_test, y_pred)

    # Accuracy interpretation
    if mape < 10:
        accuracy_level = 'Excellent'
    elif mape < 20:
        accuracy_level = 'Good'
    elif mape < 30:
        accuracy_level = 'Fair'
    else:
        accuracy_level = 'Poor'

    return {
        'product_id': product_id,
        'test_samples': len(y_test),
        'mape': round(mape, 2),
        'rmse': round(rmse, 2),
        'mae': round(mae, 2),
        'r_squared': round(r2, 4),
        'accuracy_level': accuracy_level,
        'model_confidence': 'high' if mape < 20 else 'medium' if mape < 30 else 'low',
        'actual_avg': round(np.mean(y_test), 2),
        'predicted_avg': round(np.mean(y_pred), 2)
    }


def get_sales_forecast_with_confidence(product_id, days=FORECAST_DAYS):
    """
    Generate forecast with confidence intervals.

    Provides upper and lower bounds for predictions to account for uncertainty.

    Args:
        product_id: ID of the product
        days: Number of days to forecast

    Returns:
        dict: Forecast with confidence intervals
    """
    base_forecast = generate_forecast(product_id, days)

    if 'error' in base_forecast:
        return base_forecast

    # Calculate confidence interval based on historical volatility
    df = get_historical_sales_data(product_id)

    if df is not None and len(df) >= 10:
        # Calculate standard deviation of recent data
        recent_std = df.tail(30)['total_quantity'].std() if len(df) >= 30 else df['total_quantity'].std()
        mean_demand = df['total_quantity'].mean()

        # Confidence interval width (95% confidence ≈ 2 standard deviations)
        ci_width = 2 * recent_std

        daily_forecast_with_ci = []
        for day in base_forecast['daily_forecast']:
            pred = day['predicted_quantity']
            lower = max(0, int(round(pred - ci_width)))
            upper = int(round(pred + ci_width))

            daily_forecast_with_ci.append({
                'date': day['date'],
                'predicted_quantity': pred,
                'lower_bound': lower,
                'upper_bound': upper,
                'range': upper - lower
            })

        base_forecast['daily_forecast'] = daily_forecast_with_ci
        base_forecast['has_confidence_intervals'] = True
        base_forecast['confidence_level'] = 95
        base_forecast['average_uncertainty'] = round(ci_width, 2)

    return base_forecast


def get_comprehensive_product_report(product_id):
    """
    Generate a comprehensive report combining forecast, trend analysis, and accuracy.

    Args:
        product_id: ID of the product

    Returns:
        dict: Comprehensive product report
    """
    from .models import Product

    product = Product.objects.get(id=product_id)

    # Get all components
    forecast = get_sales_forecast_with_confidence(product_id)
    trend_analysis = calculate_trend_analysis(product_id)
    accuracy = calculate_model_accuracy(product_id)
    historical = get_historical_sales_for_chart(product_id, days=90)

    # Compile report
    report = {
        'product_info': {
            'id': product.id,
            'name': product.name,
            'category': product.get_category_display(),
            'current_stock': product.current_stock,
            'safety_stock': product.safety_stock,
            'price': float(product.price)
        },
        'forecast': forecast,
        'trend_analysis': trend_analysis if 'error' not in trend_analysis else None,
        'model_accuracy': accuracy if 'error' not in accuracy else None,
        'historical_data': historical,
        'report_generated_at': datetime.now().isoformat()
    }

    return report
