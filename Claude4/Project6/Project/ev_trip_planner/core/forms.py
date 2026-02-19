from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Vehicle, ChargingStation


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'profile_picture']


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'year', 'ev_type', 'battery_capacity', 'range_km', 'charging_speed']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 2010, 'max': 2030}),
            'range_km': forms.NumberInput(attrs={'min': 50, 'max': 600}),
        }


class ChargingStationSearchForm(forms.Form):
    SEARCH_CHOICES = [
        ('all', 'All Stations'),
        ('fast', 'Fast Charging Only'),
        ('available', 'Available Now'),
    ]

    search_query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search by location or name...',
        'class': 'form-control'
    }))
    connector_type = forms.ChoiceField(choices=[('', 'All Connectors')] + ChargingStation.CONNECTOR_TYPES,
                                      required=False)
    fast_charging = forms.ChoiceField(choices=SEARCH_CHOICES, required=False)
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'placeholder': 'Max price per kWh',
        'min': 0,
        'step': 0.01,
        'class': 'form-control'
    }))
