from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Vehicle(models.Model):
    """
    Fleet Vehicle Model
    Stores vehicle information including identification and specifications
    """
    VEHICLE_TYPES = [
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('motorcycle', 'Motorcycle'),
        ('bus', 'Bus'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'In Maintenance'),
        ('inactive', 'Inactive'),
        ('retired', 'Retired'),
    ]

    vin = models.CharField(max_length=17, unique=True, verbose_name='VIN')
    plate = models.CharField(max_length=20, unique=True, verbose_name='License Plate')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, verbose_name='Vehicle Type')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    purchase_date = models.DateField(verbose_name='Purchase Date')
    current_mileage = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                          validators=[MinValueValidator(0)],
                                          verbose_name='Current Mileage')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    fuel_capacity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                        verbose_name='Fuel Capacity (gallons)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.plate})"

    @property
    def total_distance(self):
        """Calculate total distance traveled from all trips"""
        return self.trip_set.aggregate(total=models.Sum('distance'))['total'] or 0

    @property
    def total_fuel_used(self):
        """Calculate total fuel consumed from all trips"""
        return self.trip_set.aggregate(total=models.Sum('fuel_used'))['total'] or 0

    @property
    def fuel_efficiency(self):
        """Calculate fuel efficiency (miles per gallon)"""
        if self.total_fuel_used > 0:
            return round(self.total_distance / self.total_fuel_used, 2)
        return 0

    @property
    def total_maintenance_cost(self):
        """Calculate total maintenance cost"""
        return self.maintenancerecord_set.aggregate(total=models.Sum('cost'))['total'] or 0

    @property
    def cost_per_mile(self):
        """Calculate cost per mile including maintenance and fuel costs"""
        total_miles = float(self.total_distance)
        if total_miles > 0:
            maintenance_cost = float(self.total_maintenance_cost)
            # Assuming average fuel cost of $3.50 per gallon
            fuel_cost = float(self.total_fuel_used) * 3.50
            return round((maintenance_cost + fuel_cost) / total_miles, 2)
        return 0

    @property
    def last_maintenance_date(self):
        """Get the most recent maintenance date"""
        last_maintenance = self.maintenancerecord_set.order_by('-date').first()
        return last_maintenance.date if last_maintenance else None

    @property
    def active_alerts_count(self):
        """Count active alerts for this vehicle"""
        return self.alert_set.filter(is_active=True).count()


class Driver(models.Model):
    """
    Driver Model
    Stores driver information
    """
    LICENSE_TYPES = [
        ('class_a', 'Class A (CDL)'),
        ('class_b', 'Class B (CDL)'),
        ('class_c', 'Class C'),
        ('motorcycle', 'Motorcycle'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('suspended', 'Suspended'),
    ]

    name = models.CharField(max_length=200, verbose_name='Full Name')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=50, unique=True, verbose_name='License Number')
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPES, verbose_name='License Type')
    license_expiry = models.DateField(verbose_name='License Expiry Date')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    hire_date = models.DateField(verbose_name='Hire Date', default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'

    def __str__(self):
        return f"{self.name} ({self.license_number})"

    @property
    def total_trips(self):
        """Calculate total trips completed by this driver"""
        return self.trip_set.count()

    @property
    def total_distance_driven(self):
        """Calculate total distance driven by this driver"""
        return self.trip_set.aggregate(total=models.Sum('distance'))['total'] or 0


class Trip(models.Model):
    """
    Trip Model
    Stores trip records including distance, fuel consumption, and duration
    """
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('scheduled', 'Scheduled'),
        ('cancelled', 'Cancelled'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name='Vehicle')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Driver')
    start_date = models.DateTimeField(verbose_name='Start Date/Time')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='End Date/Time')
    distance = models.DecimalField(max_digits=10, decimal_places=2,
                                   validators=[MinValueValidator(0)],
                                   verbose_name='Distance (miles)')
    fuel_used = models.DecimalField(max_digits=8, decimal_places=2,
                                    validators=[MinValueValidator(0)],
                                    verbose_name='Fuel Used (gallons)')
    start_location = models.CharField(max_length=200, verbose_name='Start Location')
    end_location = models.CharField(max_length=200, verbose_name='End Location')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, verbose_name='Trip Notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'

    def __str__(self):
        return f"{self.vehicle.plate} - {self.start_location} to {self.end_location} ({self.start_date.date()})"

    @property
    def duration_hours(self):
        """Calculate trip duration in hours"""
        if self.end_date and self.start_date:
            delta = self.end_date - self.start_date
            return round(delta.total_seconds() / 3600, 2)
        return 0

    @property
    def average_speed(self):
        """Calculate average speed in mph"""
        if self.duration_hours > 0:
            return round(float(self.distance) / self.duration_hours, 2)
        return 0

    @property
    def fuel_efficiency(self):
        """Calculate fuel efficiency for this trip (miles per gallon)"""
        if self.fuel_used > 0:
            return round(float(self.distance) / float(self.fuel_used), 2)
        return 0


class MaintenanceRecord(models.Model):
    """
    Maintenance Record Model
    Stores vehicle maintenance history
    """
    MAINTENANCE_TYPES = [
        ('routine', 'Routine Service'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('emergency', 'Emergency Repair'),
        ('preventive', 'Preventive Maintenance'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name='Vehicle')
    date = models.DateTimeField(verbose_name='Maintenance Date/Time')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES,
                                        verbose_name='Maintenance Type')
    mileage_at_service = models.DecimalField(max_digits=10, decimal_places=2,
                                            validators=[MinValueValidator(0)],
                                            verbose_name='Mileage at Service')
    cost = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(0)],
                               verbose_name='Cost ($)')
    description = models.TextField(verbose_name='Description')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='low',
                               verbose_name='Severity')
    performed_by = models.CharField(max_length=200, verbose_name='Performed By')
    parts_replaced = models.TextField(blank=True, verbose_name='Parts Replaced')
    next_maintenance_mileage = models.DecimalField(max_digits=10, decimal_places=2,
                                                   null=True, blank=True,
                                                   validators=[MinValueValidator(0)],
                                                   verbose_name='Next Maintenance Mileage')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Maintenance Record'
        verbose_name_plural = 'Maintenance Records'

    def __str__(self):
        return f"{self.vehicle.plate} - {self.maintenance_type} on {self.date.date()}"


class Alert(models.Model):
    """
    Alert Model
    Stores vehicle alerts and notifications
    """
    ALERT_TYPES = [
        ('maintenance_due', 'Maintenance Due'),
        ('maintenance_overdue', 'Maintenance Overdue'),
        ('low_efficiency', 'Low Efficiency'),
        ('high_mileage', 'High Mileage'),
        ('license_expiry', 'License Expiring'),
        ('safety', 'Safety Concern'),
        ('other', 'Other'),
    ]

    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('emergency', 'Emergency'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name='Vehicle',
                               related_name='alerts')
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES, verbose_name='Alert Type')
    message = models.TextField(verbose_name='Alert Message')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info',
                              verbose_name='Severity')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    resolved_date = models.DateTimeField(null=True, blank=True, verbose_name='Resolved Date')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'

    def __str__(self):
        return f"{self.vehicle.plate} - {self.alert_type} ({self.severity})"

    def resolve(self):
        """Mark alert as resolved"""
        self.is_active = False
        self.resolved_date = timezone.now()
        self.save()
