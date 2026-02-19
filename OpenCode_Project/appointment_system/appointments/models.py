from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider')
    services = models.ManyToManyField(Service, related_name='providers')
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='provider_profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    @property
    def upcoming_appointments(self):
        return self.appointments.filter(
            status__in=['PENDING', 'CONFIRMED'],
            appointment_date__gte=timezone.now().date()
        ).count()

class TimeSlot(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        return f"{self.provider} - {day_name} {self.start_time} to {self.end_time}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'), ('COMPLETED', 'Completed'),
        ('NO_SHOW', 'No Show'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-start_time']
    
    def __str__(self):
        return f"{self.client.username} - {self.service.name} on {self.appointment_date}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'), ('COMPLETED', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.user.username}"

class Reminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('EMAIL', 'Email'), ('SMS', 'SMS'), ('PUSH', 'Push Notification'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    scheduled_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reminder for {self.appointment} - {self.get_reminder_type_display()}"
