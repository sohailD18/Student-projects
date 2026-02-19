from django import forms
from .models import Trip


class TripPlannerForm(forms.Form):
    """Form for planning a trip"""
    start_location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter starting location',
            'id': 'start_location'
        })
    )
    destination = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter destination',
            'id': 'destination'
        })
    )
    vehicle = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    battery_percent = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current battery % (0-100)',
            'min': 0,
            'max': 100
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_authenticated and hasattr(user, 'vehicles'):
            vehicle_choices = [(v.id, f"{v.year} {v.make} {v.model}") for v in user.vehicles.all()]
            if vehicle_choices:
                self.fields['vehicle'].choices = [('', 'Select your vehicle')] + vehicle_choices
            else:
                self.fields['vehicle'].choices = [('', 'No vehicles - Add one first')]
                self.fields['vehicle'].widget.attrs['disabled'] = 'disabled'
        else:
            self.fields['vehicle'].choices = [('', 'Select your vehicle')]
            self.fields['vehicle'].widget.attrs['disabled'] = 'disabled'


class TripNotesForm(forms.ModelForm):
    """Form for adding notes to a trip"""
    class Meta:
        model = Trip
        fields = ['notes', 'travel_date']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add trip notes...'
            }),
            'travel_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
