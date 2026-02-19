"""
Database models for Carbon Credit Tracking System.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Industry(models.Model):
    """
    Represents an industry company that tracks carbon emissions.
    """
    INDUSTRY_TYPES = [
        ('manufacturing', 'Manufacturing'),
        ('energy', 'Energy & Power'),
        ('chemical', 'Chemical'),
        ('cement', 'Cement'),
        ('steel', 'Steel & Iron'),
        ('textile', 'Textile'),
        ('automotive', 'Automotive'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200, unique=True)
    industry_type = models.CharField(max_length=50, choices=INDUSTRY_TYPES)
    emission_limit = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Annual carbon emission limit in tons CO2"
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Industries'

    def __str__(self):
        return self.name

    @property
    def total_emissions(self):
        """Calculate total emissions for the current year."""
        current_year = timezone.now().year
        return self.emission_records.filter(
            year=current_year
        ).aggregate(total=models.Sum('emission_amount'))['total'] or 0

    @property
    def carbon_surplus(self):
        """Calculate carbon surplus (positive = under limit, negative = over limit)."""
        return self.emission_limit - self.total_emissions

    @property
    def efficiency_score(self):
        """Calculate efficiency as percentage of limit used."""
        if self.emission_limit > 0:
            return round((self.total_emissions / self.emission_limit) * 100, 2)
        return 0


class EmissionRecord(models.Model):
    """
    Historical emission data for an industry.
    """
    industry = models.ForeignKey(
        Industry,
        on_delete=models.CASCADE,
        related_name='emission_records'
    )
    year = models.IntegerField()
    month = models.IntegerField()
    emission_amount = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Emission amount in tons CO2"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['industry', 'year', 'month']
        verbose_name_plural = 'Emission Records'

    def __str__(self):
        return f"{self.industry.name} - {self.year}/{self.month}: {self.emission_amount} tons"


class CarbonPrice(models.Model):
    """
    Historical carbon credit price data.
    """
    date = models.DateField(unique=True)
    price_per_ton = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Price per ton of carbon credit in USD"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Carbon Prices'

    def __str__(self):
        return f"${self.price_per_ton:.2f}/ton on {self.date}"


class PredictionLog(models.Model):
    """
    Log of AI predictions for tracking and audit purposes.
    """
    industry = models.ForeignKey(
        Industry,
        on_delete=models.CASCADE,
        related_name='prediction_logs'
    )
    prediction_date = models.DateTimeField(auto_now_add=True)
    predicted_emission = models.FloatField(help_text="Predicted emission in tons CO2")
    prediction_month = models.IntegerField()
    prediction_year = models.IntegerField()
    trading_suggestion = models.CharField(max_length=20)
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Model confidence score (0-1)"
    )

    class Meta:
        ordering = ['-prediction_date']
        verbose_name_plural = 'Prediction Logs'

    def __str__(self):
        return f"{self.industry.name} - {self.prediction_month}/{self.prediction_year}: {self.trading_suggestion}"
