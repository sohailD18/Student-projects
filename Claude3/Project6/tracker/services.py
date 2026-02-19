"""
AI/ML Services for Carbon Credit Analysis and Trading Support System.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from .models import Industry, EmissionRecord, CarbonPrice, PredictionLog


def get_historical_emissions(industry_id, months_back=24):
    """
    Retrieve historical emission data for an industry.

    Args:
        industry_id: ID of the industry
        months_back: Number of months of historical data to retrieve

    Returns:
        List of dictionaries with year, month, and emission_amount
    """
    records = EmissionRecord.objects.filter(
        industry_id=industry_id
    ).order_by('-year', '-month')[:months_back]

    return list(records.reverse().values('year', 'month', 'emission_amount'))


def prepare_training_data(historical_data):
    """
    Prepare data for machine learning model training.

    Args:
        historical_data: List of emission records

    Returns:
        X (features), y (targets), and scaler for predictions
    """
    if len(historical_data) < 3:
        return None, None, None

    # Convert to time-based features
    X = []
    y = []

    for i, record in enumerate(historical_data):
        # Create time-based features
        month_num = record['month']
        year_num = record['year']

        # Create feature vector: [month_sin, month_cos, year_progress, rolling_avg]
        month_sin = np.sin(2 * np.pi * month_num / 12)
        month_cos = np.cos(2 * np.pi * month_num / 12)

        # Calculate rolling average up to this point
        if i > 0:
            rolling_avg = sum(r['emission_amount'] for r in historical_data[:i+1]) / (i + 1)
        else:
            rolling_avg = record['emission_amount']

        X.append([month_sin, month_cos, year_num, rolling_avg])
        y.append(record['emission_amount'])

    X = np.array(X)
    y = np.array(y)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler


def predict_future_emissions(industry_id, months_to_predict=3):
    """
    Use Linear Regression to predict future emissions for an industry.

    Args:
        industry_id: ID of the industry
        months_to_predict: Number of future months to predict

    Returns:
        Dictionary with predictions and metadata
    """
    try:
        industry = Industry.objects.get(id=industry_id)
    except Industry.DoesNotExist:
        return {
            'success': False,
            'error': 'Industry not found',
            'predictions': []
        }

    # Get historical data
    historical_data = get_historical_emissions(industry_id, months_back=24)

    if len(historical_data) < 3:
        return {
            'success': False,
            'error': 'Insufficient historical data for prediction',
            'predictions': [],
            'historical_data': historical_data
        }

    # Prepare training data
    X, y, scaler = prepare_training_data(historical_data)

    if X is None:
        return {
            'success': False,
            'error': 'Unable to prepare training data',
            'predictions': [],
            'historical_data': historical_data
        }

    # Train model
    model = LinearRegression()
    model.fit(X, y)

    # Calculate model confidence (R² score)
    confidence_score = model.score(X, y)

    # Generate future predictions
    predictions = []
    last_record = historical_data[-1]

    # Get rolling average for last month
    rolling_avg = sum(r['emission_amount'] for r in historical_data) / len(historical_data)

    for i in range(1, months_to_predict + 1):
        # Calculate next month/year
        next_month = last_record['month'] + i
        next_year = last_record['year']

        if next_month > 12:
            next_month = next_month - 12
            next_year += 1

        # Create features for prediction
        month_sin = np.sin(2 * np.pi * next_month / 12)
        month_cos = np.cos(2 * np.pi * next_month / 12)

        # Update rolling average with previous predictions
        if predictions:
            new_avg = (rolling_avg * len(historical_data) +
                      sum(p['predicted_emission'] for p in predictions)) / (len(historical_data) + len(predictions))
            rolling_avg = new_avg

        features = np.array([[month_sin, month_cos, next_year, rolling_avg]])
        features_scaled = scaler.transform(features)

        # Make prediction
        predicted_emission = max(0, model.predict(features_scaled)[0])

        predictions.append({
            'month': next_month,
            'year': next_year,
            'predicted_emission': round(predicted_emission, 2)
        })

    return {
        'success': True,
        'industry_id': industry_id,
        'industry_name': industry.name,
        'emission_limit': industry.emission_limit,
        'confidence_score': round(confidence_score, 4),
        'predictions': predictions,
        'historical_data': historical_data[-6:]  # Last 6 months for context
    }


def get_trading_suggestion(predicted_emission, emission_limit, current_emission=0):
    """
    Generate trading suggestion based on predictions.

    Args:
        predicted_emission: Predicted emission amount
        emission_limit: Industry's emission limit
        current_emission: Current year's emission total (optional)

    Returns:
        Dictionary with suggestion and details
    """
    # Calculate projected surplus/deficit
    total_projected = current_emission + predicted_emission
    surplus = emission_limit - total_projected

    # Calculate percentage of limit used
    percentage_used = (total_projected / emission_limit) * 100 if emission_limit > 0 else 0

    # Generate suggestion
    if surplus > emission_limit * 0.1:  # More than 10% surplus
        suggestion = 'SELL'
        message = (f"Projected surplus of {surplus:.2f} tons. "
                  f"Consider selling carbon credits to optimize portfolio.")
        urgency = 'low'
    elif surplus < 0:  # Deficit
        deficit = abs(surplus)
        if deficit > emission_limit * 0.2:  # More than 20% over limit
            suggestion = 'BUY'
            message = (f"Projected deficit of {deficit:.2f} tons. "
                      f"URGENT: Purchase carbon credits immediately to avoid penalties.")
            urgency = 'high'
        else:
            suggestion = 'BUY'
            message = (f"Projected deficit of {deficit:.2f} tons. "
                      f"Consider purchasing carbon credits to stay within limit.")
            urgency = 'medium'
    elif surplus > 0:  # Small surplus
        suggestion = 'HOLD'
        message = (f"Small surplus of {surplus:.2f} tons. "
                  f"Monitor emissions closely. Consider holding credits.")
        urgency = 'low'
    else:  # At limit
        suggestion = 'HOLD'
        message = "Emissions projected at limit. Maintain current strategy."
        urgency = 'medium'

    return {
        'suggestion': suggestion,
        'message': message,
        'urgency': urgency,
        'surplus_deficit': round(surplus, 2),
        'percentage_used': round(percentage_used, 2),
        'total_projected': round(total_projected, 2)
    }


def get_carbon_price_trend(days=30):
    """
    Analyze carbon price trends.

    Args:
        days: Number of days to analyze

    Returns:
        Dictionary with price trend analysis
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    prices = CarbonPrice.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')

    if len(prices) < 2:
        return {
            'success': False,
            'error': 'Insufficient price data'
        }

    price_list = [p.price_per_ton for p in prices]

    # Calculate trend
    start_price = price_list[0]
    end_price = price_list[-1]
    price_change = end_price - start_price
    price_change_percent = (price_change / start_price) * 100 if start_price > 0 else 0

    # Calculate average and volatility
    avg_price = sum(price_list) / len(price_list)
    volatility = (max(price_list) - min(price_list)) / avg_price * 100 if avg_price > 0 else 0

    # Determine trend direction
    if price_change_percent > 2:
        trend = 'rising'
        advice = 'Prices rising. Consider selling credits now for maximum value.'
    elif price_change_percent < -2:
        trend = 'falling'
        advice = 'Prices falling. Good opportunity to purchase credits.'
    else:
        trend = 'stable'
        advice = 'Prices stable. Maintain current trading strategy.'

    return {
        'success': True,
        'trend': trend,
        'current_price': round(end_price, 2),
        'average_price': round(avg_price, 2),
        'price_change': round(price_change, 2),
        'price_change_percent': round(price_change_percent, 2),
        'volatility': round(volatility, 2),
        'advice': advice,
        'price_history': [
            {'date': p.date.isoformat(), 'price': p.price_per_ton}
            for p in prices
        ]
    }


def analyze_industry_performance():
    """
    Compare performance across all industries.

    Returns:
        Dictionary with industry comparison data
    """
    industries = Industry.objects.all()

    analysis = []
    for industry in industries:
        current_year = datetime.now().year
        total_emissions = industry.emission_records.filter(
            year=current_year
        ).aggregate(total=models.Sum('emission_amount'))['total'] or 0

        efficiency = (total_emissions / industry.emission_limit * 100) if industry.emission_limit > 0 else 0
        surplus = industry.emission_limit - total_emissions

        analysis.append({
            'id': industry.id,
            'name': industry.name,
            'industry_type': industry.industry_type,
            'emission_limit': industry.emission_limit,
            'total_emissions': round(total_emissions, 2),
            'surplus': round(surplus, 2),
            'efficiency': round(efficiency, 2),
            'status': 'under_limit' if surplus >= 0 else 'over_limit'
        })

    # Sort by efficiency
    analysis.sort(key=lambda x: x['efficiency'])

    return {
        'success': True,
        'industries': analysis,
        'total_industries': len(analysis),
        'average_efficiency': round(sum(i['efficiency'] for i in analysis) / len(analysis), 2) if analysis else 0
    }


def log_prediction(industry_id, prediction_data, trading_suggestion):
    """
    Log prediction to database for audit and tracking.

    Args:
        industry_id: ID of the industry
        prediction_data: Dictionary containing prediction details
        trading_suggestion: Dictionary containing trading suggestion

    Returns:
        PredictionLog object
    """
    # Use the first prediction for logging
    pred = prediction_data['predictions'][0] if prediction_data.get('predictions') else None

    if pred:
        log = PredictionLog.objects.create(
            industry_id=industry_id,
            predicted_emission=pred['predicted_emission'],
            prediction_month=pred['month'],
            prediction_year=pred['year'],
            trading_suggestion=trading_suggestion['suggestion'],
            confidence_score=prediction_data.get('confidence_score')
        )
        return log
    return None


from django.db import models  # Import for aggregate function
