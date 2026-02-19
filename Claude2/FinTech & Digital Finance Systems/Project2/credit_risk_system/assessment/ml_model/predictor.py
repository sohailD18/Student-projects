"""
ML Prediction Engine for Credit Risk Assessment
Uses RandomForestClassifier with synthetic data training
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import pickle

# Get the directory of this file
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
ENCODER_PATH = os.path.join(MODEL_DIR, 'encoder.pkl')


class CreditRiskPredictor:
    """
    Credit Risk Prediction Model
    Trains on synthetic data and predicts loan default probability
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_names = None

        # Try to load existing model, or train new one
        if self._load_model():
            print("Loaded existing trained model")
        else:
            print("Training new model with synthetic data...")
            self._train_model()

    def _generate_synthetic_data(self, n_samples=1000):
        """
        Generate synthetic credit risk data for training

        Features:
        - annual_income: Income distribution
        - employment_status: Categorical
        - years_employed: Years at current job
        - debt_to_income_ratio: DTI percentage
        - credit_score: Credit score (300-850)
        - num_open_loans: Number of active loans
        - num_credit_lines: Number of credit lines
        - late_payments: Late payments in last 2 years
        - bankruptcies: Boolean (0 or 1)
        - home_ownership_status: Categorical

        Target:
        - default_risk: 0 (low risk) or 1 (high risk)
        """
        np.random.seed(42)

        # Generate synthetic features
        data = {
            'annual_income': np.random.lognormal(10.5, 0.6, n_samples).clip(20000, 500000),
            'employment_status': np.random.choice(
                ['employed', 'self_employed', 'unemployed', 'retired', 'student'],
                n_samples,
                p=[0.6, 0.15, 0.1, 0.1, 0.05]
            ),
            'years_employed': np.random.exponential(5, n_samples).clip(0, 40).astype(int),
            'debt_to_income_ratio': np.random.beta(2, 5, n_samples) * 100,
            'credit_score': np.random.normal(650, 100, n_samples).clip(300, 850).astype(int),
            'num_open_loans': np.random.poisson(2, n_samples).clip(0, 10),
            'num_credit_lines': np.random.poisson(4, n_samples).clip(1, 15),
            'late_payments': np.random.poisson(1, n_samples).clip(0, 10),
            'bankruptcies': np.random.choice([0, 1], n_samples, p=[0.92, 0.08]),
            'home_ownership_status': np.random.choice(
                ['rent', 'mortgage', 'own', 'other'],
                n_samples,
                p=[0.35, 0.45, 0.15, 0.05]
            ),
        }

        df = pd.DataFrame(data)

        # Calculate risk score based on features (rule-based for synthetic labels)
        # Lower score = higher risk
        risk_score = (
            (df['credit_score'] / 850) * 30 +  # Credit score: 30% weight
            (100 - df['debt_to_income_ratio']) / 100 * 20 +  # DTI: 20% weight (lower is better)
            (df['years_employed'] / 40) * 10 +  # Employment stability: 10% weight
            (10 - df['late_payments']) / 10 * 15 +  # Payment history: 15% weight
            (1 - df['bankruptcies']) * 15 +  # Bankruptcy: 15% weight
            (df['num_open_loans'] < 5) * 10  # Number of loans: 10% weight
        )

        # Adjust based on employment and home ownership
        risk_score += (df['employment_status'] == 'employed').astype(int) * 5
        risk_score += (df['employment_status'] == 'retired').astype(int) * 3
        risk_score += (df['home_ownership_status'] == 'own').astype(int) * 5
        risk_score += (df['home_ownership_status'] == 'mortgage').astype(int) * 3

        # Normalize to 0-100
        risk_score = (risk_score / 100) * 100

        # Create binary target: 1 if risk score < 50 (high risk of default), 0 otherwise
        df['default_risk'] = (risk_score < 50).astype(int)

        # Add some randomness to make it more realistic
        noise = np.random.normal(0, 0.1, n_samples)
        df['default_risk'] = ((df['default_risk'] + noise) > 0.5).astype(int)

        return df

    def _preprocess_data(self, df, fit_encoders=True):
        """
        Preprocess data for ML model
        - Encode categorical variables
        - Scale numerical variables
        """
        df_processed = df.copy()

        # Categorical columns to encode
        categorical_cols = ['employment_status', 'home_ownership_status']

        # Numerical columns to scale
        numerical_cols = [
            'annual_income', 'years_employed', 'debt_to_income_ratio',
            'credit_score', 'num_open_loans', 'num_credit_lines',
            'late_payments', 'bankruptcies'
        ]

        # Encode categorical variables
        for col in categorical_cols:
            if fit_encoders:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_processed[col + '_encoded'] = self.label_encoders[col].fit_transform(df_processed[col])
                else:
                    df_processed[col + '_encoded'] = self.label_encoders[col].transform(df_processed[col])
            else:
                if col in self.label_encoders:
                    df_processed[col + '_encoded'] = self.label_encoders[col].transform(df_processed[col])
                else:
                    # Handle unseen categories
                    df_processed[col + '_encoded'] = 0

        # Scale numerical variables
        if fit_encoders:
            if self.scaler is None:
                self.scaler = StandardScaler()
                df_processed[numerical_cols] = self.scaler.fit_transform(df_processed[numerical_cols])
            else:
                df_processed[numerical_cols] = self.scaler.transform(df_processed[numerical_cols])
        else:
            if self.scaler is not None:
                df_processed[numerical_cols] = self.scaler.transform(df_processed[numerical_cols])

        # Prepare final feature set
        feature_cols = numerical_cols + [col + '_encoded' for col in categorical_cols]

        return df_processed[feature_cols]

    def _train_model(self):
        """Train the RandomForestClassifier on synthetic data"""
        # Generate synthetic data
        df = self._generate_synthetic_data(n_samples=1000)

        # Prepare features and target
        X = df.drop(['default_risk', 'employment_status', 'home_ownership_status'], axis=1)
        y = df['default_risk']

        # Preprocess
        X_processed = self._preprocess_data(df, fit_encoders=True)
        self.feature_names = X_processed.columns.tolist()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )

        self.model.fit(X_train, y_train)

        # Calculate and print accuracy
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        print(f"Model trained successfully!")
        print(f"Training accuracy: {train_score:.4f}")
        print(f"Test accuracy: {test_score:.4f}")

        # Save model
        self._save_model()

        return True

    def _save_model(self):
        """Save trained model, scaler, and encoders to disk"""
        try:
            joblib.dump(self.model, MODEL_PATH)
            joblib.dump(self.scaler, SCALER_PATH)

            with open(ENCODER_PATH, 'wb') as f:
                pickle.dump(self.label_encoders, f)

            print(f"Model saved to {MODEL_PATH}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False

    def _load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)

                with open(ENCODER_PATH, 'rb') as f:
                    self.label_encoders = pickle.load(f)

                # Load feature names
                if hasattr(self.model, 'feature_names_in_'):
                    self.feature_names = self.model.feature_names_in_.tolist()

                return True
        except Exception as e:
            print(f"Error loading model: {e}")

        return False

    def predict(self, applicant_data):
        """
        Predict default probability for an applicant

        Args:
            applicant_data (dict): Dictionary containing applicant information
                Required keys:
                - annual_income (float)
                - employment_status (str)
                - years_employed (int)
                - debt_to_income_ratio (float)
                - credit_score (int)
                - num_open_loans (int)
                - num_credit_lines (int)
                - late_payments (int)
                - bankruptcies (int/bool)
                - home_ownership_status (str)

        Returns:
            float: Probability of default (0.0 to 1.0)
        """
        if self.model is None:
            raise ValueError("Model not trained. Please train the model first.")

        # Create DataFrame from input
        df = pd.DataFrame([applicant_data])

        # Preprocess
        X = self._preprocess_data(df, fit_encoders=False)

        # Ensure feature order matches training
        if self.feature_names:
            X = X[self.feature_names]

        # Predict probability
        probability = self.model.predict_proba(X)[0]

        # Return probability of class 1 (default risk)
        return float(probability[1])

    def get_feature_importance(self):
        """
        Get feature importance from the trained model

        Returns:
            dict: Feature names and their importance scores
        """
        if self.model is None:
            return {}

        importance = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importance))

        # Sort by importance
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))


# Singleton instance
_predictor_instance = None


def get_predictor():
    """Get or create the singleton predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = CreditRiskPredictor()
    return _predictor_instance


# Convenience function
def predict_default_risk(applicant_data):
    """
    Convenience function to predict default risk

    Args:
        applicant_data (dict): Applicant information

    Returns:
        float: Probability of default (0.0 to 1.0)
    """
    predictor = get_predictor()
    return predictor.predict(applicant_data)


if __name__ == "__main__":
    # Test the predictor
    print("Testing Credit Risk Predictor...")

    predictor = get_predictor()

    # Test case 1: Low risk applicant
    low_risk_applicant = {
        'annual_income': 85000,
        'employment_status': 'employed',
        'years_employed': 8,
        'debt_to_income_ratio': 25,
        'credit_score': 780,
        'num_open_loans': 1,
        'num_credit_lines': 4,
        'late_payments': 0,
        'bankruptcies': 0,
        'home_ownership_status': 'own'
    }

    risk_prob = predictor.predict(low_risk_applicant)
    print(f"\nLow Risk Applicant - Default Probability: {risk_prob:.4f}")

    # Test case 2: High risk applicant
    high_risk_applicant = {
        'annual_income': 35000,
        'employment_status': 'unemployed',
        'years_employed': 0,
        'debt_to_income_ratio': 65,
        'credit_score': 520,
        'num_open_loans': 5,
        'num_credit_lines': 8,
        'late_payments': 6,
        'bankruptcies': 1,
        'home_ownership_status': 'rent'
    }

    risk_prob = predictor.predict(high_risk_applicant)
    print(f"High Risk Applicant - Default Probability: {risk_prob:.4f}")

    # Feature importance
    print("\nFeature Importance:")
    for feature, importance in predictor.get_feature_importance().items():
        print(f"  {feature}: {importance:.4f}")
