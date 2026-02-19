"""
AI Fraud Detection Engine using Scikit-Learn.
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
from datetime import datetime
import json

from .utils import DataPreprocessor


class FraudDetectionEngine:
    """
    AI Engine for fraud detection using ensemble methods.
    """

    def __init__(self, model_type='isolation_forest'):
        """
        Initialize the fraud detection engine.

        Args:
            model_type: 'isolation_forest' or 'random_forest'
        """
        self.model_type = model_type
        self.model = None
        self.preprocessor = DataPreprocessor()
        self.is_trained = False
        self.version = "1.0.0"

        # Model parameters
        self.params = {}

    def create_model(self, **kwargs):
        """
        Create the ML model with specified parameters.
        """
        if self.model_type == 'isolation_forest':
            default_params = {
                'n_estimators': 100,
                'max_samples': 'auto',
                'contamination': 0.1,
                'random_state': 42,
                'n_jobs': -1,
            }
            params = {**default_params, **kwargs}
            self.model = IsolationForest(**params)
            self.params = params

        elif self.model_type == 'random_forest':
            default_params = {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 2,
                'min_samples_leaf': 1,
                'random_state': 42,
                'n_jobs': -1,
                'class_weight': 'balanced',
            }
            params = {**default_params, **kwargs}
            self.model = RandomForestClassifier(**params)
            self.params = params

        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        return self.model

    def train(self, X, y=None):
        """
        Train the fraud detection model.

        Args:
            X: Feature DataFrame
            y: Target labels (only needed for supervised models)

        Returns:
            Training metrics dictionary
        """
        if self.model is None:
            self.create_model()

        # Ensure X is a DataFrame
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        # Preprocess features
        if self.model_type == 'isolation_forest':
            # Unsupervised learning - fit preprocessor first
            self.preprocessor.fit(X)
            X_processed = self.preprocessor.transform(X)

            # Train model
            self.model.fit(X_processed)
            predictions = self.model.predict(X_processed)

            # Convert predictions to binary (1 for normal, -1 for anomaly)
            predictions = np.where(predictions == 1, 0, 1)

            # Generate mock metrics for Isolation Forest
            metrics = {
                'model_type': 'Isolation Forest',
                'training_samples': len(X),
                'anomaly_rate': np.mean(predictions),
            }

        else:
            # Supervised learning
            # Fit preprocessor
            self.preprocessor.fit(X)
            X_processed = self.preprocessor.transform(X)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=0.2, random_state=42, stratify=y
            )

            # Train model
            self.model.fit(X_train, y_train)

            # Make predictions
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            metrics = {
                'model_type': 'Random Forest',
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1_score': f1_score(y_test, y_pred, zero_division=0),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
            }

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            metrics['confusion_matrix'] = {
                'true_negatives': int(cm[0, 0]),
                'false_positives': int(cm[0, 1]),
                'false_negatives': int(cm[1, 0]),
                'true_positives': int(cm[1, 1]),
            }

        self.is_trained = True
        return metrics

    def predict(self, transaction_data):
        """
        Predict fraud for a single transaction.

        Args:
            transaction_data: Dictionary or DataFrame with transaction features

        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        # Convert dict to DataFrame if needed
        if isinstance(transaction_data, dict):
            df = pd.DataFrame([transaction_data])
        else:
            df = transaction_data.copy()

        # Preprocess
        df_processed = self.preprocessor.transform(df)

        # Make prediction
        if self.model_type == 'isolation_forest':
            prediction = self.model.predict(df_processed)[0]
            # Convert: 1 = normal (0), -1 = anomaly (1)
            is_fraud = 1 if prediction == -1 else 0
            # Use anomaly score as risk score
            risk_score = self.model.score_samples(df_processed)[0]
            # Normalize risk score to 0-1 (higher = more risky)
            risk_score = max(0, min(1, (0.5 - risk_score) * 2))
        else:
            is_fraud = self.model.predict(df_processed)[0]
            risk_score = self.model.predict_proba(df_processed)[0, 1]

        return {
            'is_fraud': bool(is_fraud),
            'risk_score': float(risk_score),
            'confidence': abs(risk_score - 0.5) * 2,  # Confidence in prediction
        }

    def predict_batch(self, transaction_data_list):
        """
        Predict fraud for multiple transactions.

        Args:
            transaction_data_list: List of dictionaries or DataFrame

        Returns:
            List of prediction dictionaries
        """
        predictions = []

        if isinstance(transaction_data_list, list):
            df = pd.DataFrame(transaction_data_list)
        else:
            df = transaction_data_list.copy()

        # Preprocess
        df_processed = self.preprocessor.transform(df)

        # Make predictions
        if self.model_type == 'isolation_forest':
            preds = self.model.predict(df_processed)
            scores = self.model.score_samples(df_processed)

            for pred, score in zip(preds, scores):
                is_fraud = 1 if pred == -1 else 0
                risk_score = max(0, min(1, (0.5 - score) * 2))
                predictions.append({
                    'is_fraud': bool(is_fraud),
                    'risk_score': float(risk_score),
                    'confidence': abs(risk_score - 0.5) * 2,
                })
        else:
            preds = self.model.predict(df_processed)
            probas = self.model.predict_proba(df_processed)[:, 1]

            for pred, proba in zip(preds, probas):
                predictions.append({
                    'is_fraud': bool(pred),
                    'risk_score': float(proba),
                    'confidence': abs(proba - 0.5) * 2,
                })

        return predictions

    def evaluate(self, X, y_true):
        """
        Evaluate model performance on test data.

        Args:
            X: Test features
            y_true: True labels

        Returns:
            Dictionary of evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")

        # Preprocess
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        X_processed = self.preprocessor.transform(X)

        # Make predictions
        if self.model_type == 'isolation_forest':
            predictions = self.model.predict(X_processed)
            y_pred = np.where(predictions == 1, 0, 1)
        else:
            y_pred = self.model.predict(X_processed)

        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
        }

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = {
            'true_negatives': int(cm[0, 0]),
            'false_positives': int(cm[0, 1]),
            'false_negatives': int(cm[1, 0]),
            'true_positives': int(cm[1, 1]),
        }

        return metrics

    def save(self, directory):
        """
        Save model and preprocessor to disk.
        """
        os.makedirs(directory, exist_ok=True)

        # Save model
        model_path = os.path.join(directory, 'fraud_model.joblib')
        joblib.dump(self.model, model_path)

        # Save preprocessor
        preprocessor_path = os.path.join(directory, 'preprocessor.joblib')
        self.preprocessor.save(preprocessor_path)

        # Save metadata
        metadata = {
            'model_type': self.model_type,
            'version': self.version,
            'is_trained': self.is_trained,
            'params': self.params,
            'saved_at': datetime.now().isoformat(),
        }
        metadata_path = os.path.join(directory, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def load(cls, directory):
        """
        Load model and preprocessor from disk.
        """
        # Load metadata
        metadata_path = os.path.join(directory, 'metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Create instance
        engine = cls(model_type=metadata['model_type'])
        engine.version = metadata['version']
        engine.params = metadata['params']

        # Load model
        model_path = os.path.join(directory, 'fraud_model.joblib')
        engine.model = joblib.load(model_path)

        # Load preprocessor
        preprocessor_path = os.path.join(directory, 'preprocessor.joblib')
        engine.preprocessor = DataPreprocessor.load(preprocessor_path)

        engine.is_trained = metadata['is_trained']

        return engine


def get_fraud_reasons(transaction_data, risk_score):
    """
    Generate human-readable fraud reasons based on transaction data.
    """
    reasons = []

    # Check amount
    amount = float(transaction_data.get('amount', 0))
    if amount > 1000:
        reasons.append(f"High transaction amount: ${amount:.2f}")

    # Check time
    timestamp = transaction_data.get('timestamp')
    if timestamp:
        if isinstance(timestamp, str):
            from datetime import datetime
            timestamp = pd.to_datetime(timestamp)
        hour = timestamp.hour
        if hour < 6 or hour > 23:
            reasons.append(f"Unusual time: {hour}:00")

    # Check merchant category
    merchant_category = transaction_data.get('merchant_category', '')
    if merchant_category in ['electronics', 'jewelry', 'online_services']:
        reasons.append(f"High-risk category: {merchant_category}")

    # Check location
    country = transaction_data.get('country', '')
    if country not in ['US', 'CA', 'GB', 'AU']:
        reasons.append(f"International transaction: {country}")

    if not reasons and risk_score > 0.5:
        reasons.append("Pattern anomaly detected")

    return "; ".join(reasons) if reasons else "No specific reason"


# Global model instance
_model_instance = None


def get_model():
    """
    Get or create the global model instance.
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = FraudDetectionEngine(model_type='random_forest')
    return _model_instance


def save_trained_model_metrics(metrics, model_version="1.0.0"):
    """
    Save model training metrics to database.
    """
    from .models import ModelMetrics

    # Extract confusion matrix if present
    cm = metrics.pop('confusion_matrix', {
        'true_positives': 0,
        'true_negatives': 0,
        'false_positives': 0,
        'false_negatives': 0,
    })

    # Create ModelMetrics record
    model_metric = ModelMetrics.objects.create(
        model_name=metrics.get('model_type', 'Random Forest'),
        model_version=model_version,
        accuracy=metrics.get('accuracy', 0.0),
        precision=metrics.get('precision', 0.0),
        recall=metrics.get('recall', 0.0),
        f1_score=metrics.get('f1_score', 0.0),
        true_positives=cm.get('true_positives', 0),
        true_negatives=cm.get('true_negatives', 0),
        false_positives=cm.get('false_positives', 0),
        false_negatives=cm.get('false_negatives', 0),
        training_samples=metrics.get('training_samples', 0),
        test_samples=metrics.get('test_samples', 0),
        parameters=metrics.get('params', {}),
    )

    return model_metric
