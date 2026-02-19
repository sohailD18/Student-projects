from django.forms import ModelForm, DateInput, TimeInput
from django import forms
from .models import Service, Provider, Appointment, Booking

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'special_requests']
        widgets = {
            'booking_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'booking_time': TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AppointmentForm(ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'start_time', 'notes']
        widgets = {
            'appointment_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ProviderForm(ModelForm):
    class Meta:
        model = Provider
        fields = ['bio', 'profile_image', 'phone', 'is_available']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
