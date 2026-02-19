"""
ML Utilities for Market Trend Analysis System
Handles data preprocessing, feature engineering, and ML predictions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Try to import yfinance, if not available, will use dummy data
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not available. Will use dummy data generation.")

# Try to import scikit-learn
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    SCIKIT_AVAILABLE = True
except ImportError:
    SCIKIT_AVAILABLE = False
    print("Warning: scikit-learn not available. ML features will be limited.")


class DataProcessor:
    """Class for processing stock data and calculating technical indicators"""

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data by handling missing values and outliers
        """
        # Make a copy to avoid modifying the original
        df = df.copy()

        # Forward fill missing values
        df = df.ffill()

        # Backward fill any remaining missing values
        df = df.bfill()

        # Remove outliers using IQR method
        for column in ['open', 'high', 'low', 'close', 'volume']:
            if column in df.columns:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)

        return df

    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 50]) -> pd.DataFrame:
        """
        Calculate moving averages for specified periods
        """
        df = df.copy()

        for period in periods:
            if len(df) >= period:
                df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
            else:
                df[f'ma_{period}'] = np.nan

        return df

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Relative Strength Index (RSI)
        """
        df = df.copy()

        # Calculate price changes
        delta = df['close'].diff()

        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Calculate RS and RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        return df

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """
        Calculate Bollinger Bands
        """
        df = df.copy()

        df['bb_middle'] = df['close'].rolling(window=period).mean()
        bb_std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std_dev)

        return df

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        df = df.copy()

        # Calculate EMAs
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

        # Calculate MACD line
        df['macd'] = ema_fast - ema_slow

        # Calculate signal line
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()

        # Calculate MACD histogram
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        return df

    @staticmethod
    def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily returns
        """
        df = df.copy()
        df['daily_return'] = df['close'].pct_change() * 100
        return df

    @staticmethod
    def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer all features for ML model
        """
        df = df.copy()

        # Clean data first
        df = DataProcessor.clean_data(df)

        # Calculate technical indicators
        df = DataProcessor.calculate_moving_averages(df)
        df = DataProcessor.calculate_rsi(df)
        df = DataProcessor.calculate_bollinger_bands(df)
        df = DataProcessor.calculate_macd(df)
        df = DataProcessor.calculate_returns(df)

        # Calculate price momentum
        df['momentum_5'] = df['close'].pct_change(5) * 100
        df['momentum_10'] = df['close'].pct_change(10) * 100

        # Calculate volatility
        df['volatility_10'] = df['close'].rolling(window=10).std()
        df['volatility_20'] = df['close'].rolling(window=20).std()

        # Calculate price rate of change
        df['roc'] = ((df['close'] - df['close'].shift(5)) / df['close'].shift(5)) * 100

        # Create lag features
        df['close_lag_1'] = df['close'].shift(1)
        df['close_lag_5'] = df['close'].shift(5)

        return df


class VolatilityAnalyzer:
    """Class for analyzing volatility and risk metrics"""

    @staticmethod
    def calculate_volatility(df: pd.DataFrame, period: int = 30) -> Dict:
        """
        Calculate daily and annualized volatility
        """
        if len(df) < period:
            period = len(df)

        returns = df['close'].pct_change().dropna()
        daily_volatility = returns.tail(period).std()
        annualized_volatility = daily_volatility * np.sqrt(252)

        return {
            'daily_volatility': float(daily_volatility),
            'annualized_volatility': float(annualized_volatility),
            'period_days': period
        }

    @staticmethod
    def calculate_var(df: pd.DataFrame, confidence_level: float = 0.95) -> Dict:
        """
        Calculate Value at Risk (VaR)
        """
        returns = df['close'].pct_change().dropna()

        if confidence_level == 0.95:
            var = np.percentile(returns, 5)
        elif confidence_level == 0.99:
            var = np.percentile(returns, 1)
        else:
            var = np.percentile(returns, (1 - confidence_level) * 100)

        return {
            f'var_{int(confidence_level * 100)}': float(var)
        }

    @staticmethod
    def calculate_sharpe_ratio(df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio
        """
        returns = df['close'].pct_change().dropna()
        excess_returns = returns.mean() - (risk_free_rate / 252)
        volatility = returns.std()

        if volatility == 0:
            return 0.0

        sharpe_ratio = (excess_returns / volatility) * np.sqrt(252)
        return float(sharpe_ratio)

    @staticmethod
    def calculate_max_drawdown(df: pd.DataFrame) -> float:
        """
        Calculate Maximum Drawdown
        """
        cumulative_returns = (1 + df['close'].pct_change()).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = float(drawdown.min())
        return max_drawdown

    @staticmethod
    def classify_risk_level(volatility: float) -> str:
        """
        Classify risk level based on volatility
        """
        if volatility < 0.15:
            return 'Low'
        elif volatility < 0.25:
            return 'Medium'
        elif volatility < 0.40:
            return 'High'
        else:
            return 'Very High'


class PredictionEngine:
    """ML Engine for price predictions"""

    def __init__(self, model_type: str = 'RandomForest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare features for ML model
        """
        # Select relevant features
        feature_columns = [
            'close', 'volume', 'ma_5', 'ma_10', 'ma_20', 'ma_50',
            'rsi', 'daily_return', 'momentum_5', 'momentum_10',
            'volatility_10', 'volatility_20', 'roc', 'macd', 'macd_signal',
            'close_lag_1', 'close_lag_5'
        ]

        # Filter to only include existing columns
        available_features = [col for col in feature_columns if col in df.columns]

        # Create feature dataframe
        X = df[available_features].copy()

        # Handle remaining NaN values
        X = X.ffill().bfill().fillna(0)

        self.feature_names = available_features
        return X, available_features

    def train(self, df: pd.DataFrame, target_col: str = 'close') -> Dict:
        """
        Train the ML model
        """
        if not SCIKIT_AVAILABLE:
            return {'error': 'scikit-learn not available'}

        # Prepare data
        df = df.copy()

        # Create target variable (next day's close price)
        df['target'] = df['close'].shift(-1)

        # Drop last row (no target)
        df = df.dropna()

        # Prepare features
        X, _ = self.prepare_features(df)
        y = df['target']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Initialize and train model
        if self.model_type == 'RandomForest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'LinearRegression':
            self.model = LinearRegression()
        else:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)

        self.model.fit(X_train_scaled, y_train)

        # Make predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)

        # Calculate metrics
        mse = mean_squared_error(y_test, y_test_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_test_pred)
        r2 = r2_score(y_test, y_test_pred)

        # Calculate feature importance (if available)
        feature_importance = {}
        if hasattr(self.model, 'feature_importances_'):
            for feature, importance in zip(self.feature_names, self.model.feature_importances_):
                feature_importance[feature] = float(importance)

        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2),
            'feature_importance': feature_importance,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

    def predict(self, df: pd.DataFrame) -> float:
        """
        Make a prediction for the next day's closing price
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        if not SCIKIT_AVAILABLE:
            raise ValueError("scikit-learn not available")

        # Prepare features
        X, _ = self.prepare_features(df)

        # Get the most recent data point
        latest_data = X.iloc[[-1]]

        # Scale features
        latest_scaled = self.scaler.transform(latest_data)

        # Make prediction
        prediction = self.model.predict(latest_scaled)[0]

        return float(prediction)

    def generate_signal(self, current_price: float, predicted_price: float,
                       threshold: float = 0.02) -> Dict:
        """
        Generate buy/sell signal based on prediction
        """
        price_change = (predicted_price - current_price) / current_price

        if price_change > threshold:
            signal = 'BUY'
            confidence = min(95, 50 + (price_change * 100))
        elif price_change < -threshold:
            signal = 'SELL'
            confidence = min(95, 50 + (abs(price_change) * 100))
        else:
            signal = 'HOLD'
            confidence = 50.0

        return {
            'signal': signal,
            'confidence': round(confidence, 2),
            'price_change_percent': round(price_change * 100, 2),
            'current_price': float(current_price),
            'predicted_price': float(predicted_price)
        }


class ReportGenerator:
    """Class for generating market analysis reports"""

    @staticmethod
    def generate_summary(df: pd.DataFrame, volatility: Dict, prediction: Dict) -> Dict:
        """
        Generate a comprehensive market analysis summary
        """
        latest_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2] if len(df) > 1 else latest_price

        # Calculate price trend
        price_change = ((latest_price - prev_price) / prev_price) * 100

        # Determine trend
        if price_change > 2:
            trend = 'Bullish'
        elif price_change < -2:
            trend = 'Bearish'
        elif volatility.get('daily_volatility', 0) > 0.03:
            trend = 'Volatile'
        else:
            trend = 'Sideways'

        # Generate key findings
        key_findings = [
            f"Current price: ${latest_price:.2f}",
            f"Daily change: {price_change:+.2f}%",
            f"Volatility: {volatility.get('daily_volatility', 0):.4f}",
        ]

        # RSI analysis
        if 'rsi' in df.columns:
            latest_rsi = df['rsi'].iloc[-1]
            if pd.notna(latest_rsi):
                key_findings.append(f"RSI: {latest_rsi:.2f}")
                if latest_rsi > 70:
                    key_findings.append("RSI indicates overbought conditions")
                elif latest_rsi < 30:
                    key_findings.append("RSI indicates oversold conditions")

        # Add prediction info
        if 'signal' in prediction:
            key_findings.append(f"Signal: {prediction['signal']}")
            key_findings.append(f"Predicted price: ${prediction.get('predicted_price', 0):.2f}")

        # Generate recommendation
        recommendation = ReportGenerator._generate_recommendation(
            trend, volatility.get('daily_volatility', 0), prediction
        )

        return {
            'trend': trend,
            'key_findings': key_findings,
            'recommendation': recommendation,
            'current_price': float(latest_price),
            'price_change_percent': float(price_change)
        }

    @staticmethod
    def _generate_recommendation(trend: str, volatility: float, prediction: Dict) -> str:
        """
        Generate trading recommendation based on analysis
        """
        signal = prediction.get('signal', 'HOLD')
        confidence = prediction.get('confidence', 50)

        if signal == 'BUY':
            if confidence > 70:
                return f"Strong BUY recommendation. The model predicts a {prediction.get('price_change_percent', 0):.2f}% price increase with {confidence}% confidence. Consider establishing a long position."
            else:
                return f"Moderate BUY signal. Technical indicators suggest upward momentum. Monitor closely before entering position."
        elif signal == 'SELL':
            if confidence > 70:
                return f"Strong SELL recommendation. The model predicts a {abs(prediction.get('price_change_percent', 0)):.2f}% price decrease with {confidence}% confidence. Consider reducing positions."
            else:
                return f"Moderate SELL signal. Showing bearish indicators. Use caution and consider stop-loss levels."
        else:
            return f"HOLD recommendation. Market appears to be {trend.lower()} with current volatility levels. Wait for clearer signals before making trading decisions."


def fetch_stock_data_yfinance(symbol: str, period: str = '1y') -> Optional[pd.DataFrame]:
    """
    Fetch stock data using yfinance
    """
    if not YFINANCE_AVAILABLE:
        return None

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            return None

        # Reset index and rename columns
        df = df.reset_index()
        df.columns = [col.lower() for col in df.columns]

        # Map columns
        column_mapping = {
            'date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            'adj close': 'adjusted_close'
        }

        df = df.rename(columns=column_mapping)

        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date

        return df

    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None


def generate_dummy_data(symbol: str, days: int = 252) -> pd.DataFrame:
    """
    Generate dummy stock data for testing when yfinance is not available
    """
    np.random.seed(hash(symbol) % (2**32))

    # Generate price series with random walk
    returns = np.random.normal(0.001, 0.02, days)
    prices = [100]  # Starting price

    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))

    # Create OHLC data
    dates = pd.date_range(end=datetime.now().date(), periods=days)

    data = []
    for i, date in enumerate(dates):
        close = prices[i]
        open_p = close * (1 + np.random.uniform(-0.01, 0.01))
        high = max(open_p, close) * (1 + np.random.uniform(0, 0.01))
        low = min(open_p, close) * (1 - np.random.uniform(0, 0.01))
        volume = np.random.randint(1000000, 10000000)

        data.append({
            'date': date.date(),
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'adjusted_close': close
        })

    df = pd.DataFrame(data)
    df = df.rename(columns={
        'open': 'open_price',
        'date': 'date'
    })

    return df
