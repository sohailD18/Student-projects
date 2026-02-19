from django.db import models


class Crop(models.Model):
    CROP_TYPES = [
        ('cereals', 'Cereals'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('legumes', 'Legumes'),
        ('tubers', 'Tubers'),
        ('cash_crops', 'Cash Crops'),
    ]

    SOIL_TYPE_CHOICES = [
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('loamy', 'Loamy'),
        ('silty', 'Silty'),
        ('peaty', 'Peaty'),
        ('chalky', 'Chalky'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CROP_TYPES)
    duration = models.IntegerField(help_text="Duration in days")
    suitable_seasons = models.ManyToManyField(
        'Season',
        blank=True,
        related_name='crops',
        help_text="Seasons when this crop can be grown"
    )
    suitable_soil_types = models.JSONField(
        default=list,
        blank=True,
        help_text="List of suitable soil types (e.g., ['clay', 'loamy'])"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=50, unique=True)
    months = models.CharField(max_length=100, help_text="Comma-separated months, e.g., 'June, July, August'")

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class SoilData(models.Model):
    SOIL_TYPES = [
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('loamy', 'Loamy'),
        ('silty', 'Silty'),
        ('peaty', 'Peaty'),
        ('chalky', 'Chalky'),
    ]

    ph = models.DecimalField(max_digits=4, decimal_places=2, help_text="pH level (0-14)")
    moisture = models.DecimalField(max_digits=5, decimal_places=2, help_text="Moisture percentage")
    type = models.CharField(max_length=20, choices=SOIL_TYPES)
    recorded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_date']

    def __str__(self):
        return f"Soil: {self.type} (pH: {self.ph}, Moisture: {self.moisture}%)"


class YieldRecord(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='yield_records')
    year = models.IntegerField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Yield quantity in tons/hectare")
    recorded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-recorded_date']
        verbose_name = 'Yield Record'
        verbose_name_plural = 'Yield Records'

    def __str__(self):
        return f"{self.crop.name} - {self.year}: {self.quantity} tons/ha"
