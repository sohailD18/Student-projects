"""
Data preprocessing utilities for the fraud detection system.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from datetime import datetime, timedelta
import json
import os


class DataPreprocessor:
    """
    Handles data preprocessing for the fraud detection model.
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.fitted = False

    def fit(self, df):
        """
        Fit the preprocessor on the data.
        """
        # Fit numerical scaler
        numerical_cols = ['amount', 'hour_of_day', 'day_of_week']
        self.scaler.fit(df[numerical_cols])

        # Fit label encoders for categorical columns
        categorical_cols = ['transaction_type', 'merchant_category', 'country']
        for col in categorical_cols:
            le = LabelEncoder()
            le.fit(df[col].astype(str))
            self.label_encoders[col] = le

        self.fitted = True
        return self

    def transform(self, df):
        """
        Transform the data using fitted preprocessor.
        """
        if not self.fitted:
            raise ValueError("Preprocessor must be fitted before transform")

        df_processed = df.copy()

        # Scale numerical columns
        numerical_cols = ['amount', 'hour_of_day', 'day_of_week']
        df_processed[numerical_cols] = self.scaler.transform(df[numerical_cols])

        # Encode categorical columns
        for col, le in self.label_encoders.items():
            df_processed[col] = le.transform(df[col].astype(str))

        return df_processed

    def fit_transform(self, df):
        """
        Fit and transform in one step.
        """
        return self.fit(df).transform(df)

    def get_feature_columns(self):
        """
        Return the list of feature columns used by the model.
        """
        return ['amount', 'hour_of_day', 'day_of_week',
                'transaction_type', 'merchant_category', 'country']

    def create_features_from_transaction(self, transaction_data):
        """
        Create feature array from a transaction dictionary.
        """
        # Extract timestamp features
        timestamp = transaction_data.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)

        hour_of_day = timestamp.hour
        day_of_week = timestamp.weekday()

        # Create feature dict
        features = {
            'amount': float(transaction_data.get('amount', 0)),
            'hour_of_day': hour_of_day,
            'day_of_week': day_of_week,
            'transaction_type': transaction_data.get('transaction_type', 'purchase'),
            'merchant_category': transaction_data.get('merchant_category', 'other'),
            'country': transaction_data.get('country', 'US'),
        }

        # Convert to DataFrame
        df = pd.DataFrame([features])

        # Transform if preprocessor is fitted
        if self.fitted:
            df_processed = self.transform(df)
            return df_processed.iloc[0].values
        else:
            return df.iloc[0].values

    def save(self, filepath):
        """
        Save the preprocessor to disk.
        """
        import joblib
        joblib.dump({
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'fitted': self.fitted
        }, filepath)

    @classmethod
    def load(cls, filepath):
        """
        Load a preprocessor from disk.
        """
        import joblib
        data = joblib.load(filepath)
        preprocessor = cls()
        preprocessor.scaler = data['scaler']
        preprocessor.label_encoders = data['label_encoders']
        preprocessor.fitted = data['fitted']
        return preprocessor


def extract_temporal_features(timestamp):
    """
    Extract temporal features from a timestamp.
    """
    if isinstance(timestamp, str):
        timestamp = pd.to_datetime(timestamp)

    return {
        'hour_of_day': timestamp.hour,
        'day_of_week': timestamp.weekday(),
        'day_of_month': timestamp.day,
        'month': timestamp.month,
        'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
        'is_night': 1 if timestamp.hour < 6 or timestamp.hour > 22 else 0,
    }


def calculate_amount_statistics(amount, historical_amounts):
    """
    Calculate amount-based statistics.
    """
    if not historical_amounts or len(historical_amounts) == 0:
        return {
            'amount_zscore': 0,
            'amount_percentile': 50,
            'is_large_amount': 0,
        }

    amounts_array = np.array(historical_amounts)
    mean = np.mean(amounts_array)
    std = np.std(amounts_array)

    zscore = (amount - mean) / (std + 1e-6)  # Avoid division by zero
    percentile = np.percentile(amounts_array, amount) * 100

    return {
        'amount_zscore': zscore,
        'amount_percentile': percentile,
        'is_large_amount': 1 if amount > mean + 2 * std else 0,
    }


def encode_categorical_features(data):
    """
    Encode categorical features for model input.
    """
    categorical_mapping = {
        'transaction_type': {
            'purchase': 0,
            'withdrawal': 1,
            'transfer': 2,
            'deposit': 3,
            'payment': 4,
        },
        'merchant_category': {
            'electronics': 0,
            'clothing': 1,
            'food': 2,
            'travel': 3,
            'entertainment': 4,
            'gas_station': 5,
            'online_services': 6,
            'health': 7,
            'other': 8,
        },
    }

    encoded = {}
    for feature, mapping in categorical_mapping.items():
        value = data.get(feature, 'other')
        encoded[feature] = mapping.get(value, len(mapping) - 1)

    return encoded


def normalize_features(df, feature_columns):
    """
    Normalize numerical features to 0-1 range.
    """
    df_normalized = df.copy()
    for col in feature_columns:
        if col in df.columns and df[col].dtype in ['int64', 'float64']:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df_normalized[col] = (df[col] - min_val) / (max_val - min_val)
    return df_normalized


def prepare_training_data(transactions_queryset):
    """
    Prepare training data from Django queryset.
    """
    from .models import Transaction

    # Convert queryset to DataFrame
    data = list(transactions_queryset.values(
        'amount', 'transaction_type', 'merchant_category', 'country',
        'timestamp', 'is_fraud', 'risk_score'
    ))

    if not data:
        return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(data)

    # Extract temporal features
    df['hour_of_day'] = df['timestamp'].apply(lambda x: x.hour)
    df['day_of_week'] = df['timestamp'].apply(lambda x: x.weekday())

    # Prepare features
    feature_columns = ['amount', 'hour_of_day', 'day_of_week',
                      'transaction_type', 'merchant_category', 'country']

    X = df[feature_columns].copy()
    y = df['is_fraud'].copy()

    return X, y
