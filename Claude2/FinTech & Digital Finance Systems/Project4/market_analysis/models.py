from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Stock(models.Model):
    """
    Model to store stock ticker information
    """
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=50, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']
        verbose_name_plural = 'Stocks'

    def __str__(self):
        return f"{self.symbol} - {self.company_name or 'N/A'}"

    @property
    def latest_price(self):
        """Get the most recent closing price"""
        latest = self.historical_data.order_by('-date').first()
        return latest.close if latest else None

    @property
    def data_points_count(self):
        """Get the count of historical data points"""
        return self.historical_data.count()


class HistoricalData(models.Model):
    """
    Model to store historical stock price data
    """
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='historical_data',
        db_index=True
    )
    date = models.DateField(db_index=True)
    open_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0'))]
    )
    high = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0'))]
    )
    low = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0'))]
    )
    close = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0'))]
    )
    volume = models.BigIntegerField(validators=[MinValueValidator(0)])
    adjusted_close = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))]
    )

    # Technical indicators (computed fields)
    moving_average_5 = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )
    moving_average_10 = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )
    moving_average_20 = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )
    moving_average_50 = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )
    rsi = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['stock', 'date']
        verbose_name_plural = 'Historical Data'
        indexes = [
            models.Index(fields=['stock', 'date']),
        ]

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}: ${self.close}"

    @property
    def price_change(self):
        """Calculate price change from open to close"""
        return float(self.close) - float(self.open_price)

    @property
    def price_change_percent(self):
        """Calculate percentage change from open to close"""
        if self.open_price > 0:
            return ((float(self.close) - float(self.open_price)) / float(self.open_price)) * 100
        return 0


class Prediction(models.Model):
    """
    Model to store ML predictions and model performance metrics
    """
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='predictions',
        db_index=True
    )
    prediction_date = models.DateField(db_index=True)
    target_date = models.DateField(db_index=True)

    # Prediction values
    predicted_price = models.DecimalField(max_digits=12, decimal_places=4)
    actual_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )

    # Model metrics
    model_type = models.CharField(
        max_length=50,
        default='LinearRegression',
        choices=[
            ('LinearRegression', 'Linear Regression'),
            ('RandomForest', 'Random Forest'),
            ('LSTM', 'LSTM Neural Network'),
            ('XGBoost', 'XGBoost'),
        ]
    )
    mse = models.FloatField(null=True, blank=True, help_text='Mean Squared Error')
    rmse = models.FloatField(null=True, blank=True, help_text='Root Mean Squared Error')
    r2_score = models.FloatField(null=True, blank=True, help_text='R-squared Score')
    mae = models.FloatField(null=True, blank=True, help_text='Mean Absolute Error')

    # Feature importance (stored as JSON)
    feature_importance = models.JSONField(null=True, blank=True)

    # Signal generation
    signal = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ('BUY', 'Buy Signal'),
            ('SELL', 'Sell Signal'),
            ('HOLD', 'Hold Signal'),
        ]
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text='Confidence level in percentage'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prediction_date']
        unique_together = ['stock', 'prediction_date']
        verbose_name_plural = 'Predictions'
        indexes = [
            models.Index(fields=['stock', 'prediction_date']),
        ]

    def __str__(self):
        return f"{self.stock.symbol} - Predicted: ${self.predicted_price} for {self.target_date}"

    @property
    def prediction_accuracy(self):
        """Calculate prediction accuracy percentage"""
        if self.actual_price:
            difference = abs(float(self.predicted_price) - float(self.actual_price))
            accuracy = max(0, 100 - (difference / float(self.actual_price) * 100))
            return round(accuracy, 2)
        return None


class VolatilityAnalysis(models.Model):
    """
    Model to store volatility and risk analysis results
    """
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='volatility_analyses',
        db_index=True
    )
    analysis_date = models.DateField(db_index=True)

    # Volatility metrics
    daily_volatility = models.FloatField(help_text='Standard deviation of daily returns')
    annualized_volatility = models.FloatField(help_text='Annualized volatility (252 trading days)')

    # Risk metrics
    var_95 = models.FloatField(
        null=True,
        blank=True,
        help_text='Value at Risk at 95% confidence level'
    )
    var_99 = models.FloatField(
        null=True,
        blank=True,
        help_text='Value at Risk at 99% confidence level'
    )

    # Additional metrics
    sharpe_ratio = models.FloatField(null=True, blank=True)
    max_drawdown = models.FloatField(null=True, blank=True)
    beta = models.FloatField(null=True, blank=True)

    # Risk level classification
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low Risk'),
            ('Medium', 'Medium Risk'),
            ('High', 'High Risk'),
            ('Very High', 'Very High Risk'),
        ]
    )

    # Analysis period
    period_days = models.IntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analysis_date']
        unique_together = ['stock', 'analysis_date']
        verbose_name_plural = 'Volatility Analyses'

    def __str__(self):
        return f"{self.stock.symbol} - {self.analysis_date}: {self.risk_level} Risk"


class MarketReport(models.Model):
    """
    Model to store generated market analysis reports
    """
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='market_reports',
        db_index=True
    )
    report_date = models.DateField(db_index=True)

    # Report summary
    title = models.CharField(max_length=200)
    summary = models.TextField()

    # Market trend
    trend = models.CharField(
        max_length=20,
        choices=[
            ('Bullish', 'Bullish'),
            ('Bearish', 'Bearish'),
            ('Sideways', 'Sideways'),
            ('Volatile', 'Volatile'),
        ]
    )

    # Key findings (stored as JSON)
    key_findings = models.JSONField(default=list)

    # Recommendations
    recommendation = models.TextField()

    # Report data (JSON)
    data = models.JSONField(default=dict, help_text='Additional report data')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-report_date']
        verbose_name_plural = 'Market Reports'

    def __str__(self):
        return f"{self.stock.symbol} - {self.title} ({self.report_date})"
