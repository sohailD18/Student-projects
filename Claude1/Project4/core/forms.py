from django import forms
from .models import ActivityLog, UserProfile


class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['activity_type', 'activity_subtype', 'value', 'date', 'notes']
        widgets = {
            'activity_type': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select activity type'
                }
            ),
            'activity_subtype': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select subtype'
                }
            ),
            'value': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter value',
                    'step': '0.01',
                    'min': '0'
                }
            ),
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Add notes about this activity (optional)',
                    'rows': 3
                }
            ),
        }
        labels = {
            'activity_type': 'Activity Type',
            'activity_subtype': 'Subtype',
            'value': 'Value',
            'date': 'Date',
            'notes': 'Notes'
        }
        help_texts = {
            'activity_type': 'Choose the type of eco-activity',
            'activity_subtype': 'Choose a specific subtype for more accurate calculations',
            'value': 'Enter the activity value (e.g., km for travel, kWh for energy, meals for diet)',
            'date': 'Select the date of the activity',
            'notes': 'Optional: Add any additional notes about this activity'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make activity_subtype optional
        self.fields['activity_subtype'].required = False
        self.fields['notes'].required = False

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value is not None and value <= 0:
            raise forms.ValidationError('Value must be greater than zero.')
        return value


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'avatar_url']
        widgets = {
            'bio': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Tell others about your sustainability journey',
                    'rows': 4
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Your city or region'
                }
            ),
            'avatar_url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://example.com/avatar.jpg'
                }
            ),
        }
        labels = {
            'bio': 'Bio',
            'location': 'Location',
            'avatar_url': 'Avatar URL'
        }
        help_texts = {
            'bio': 'Write a short description about your sustainability goals',
            'location': 'Share your location to connect with local eco-warriors',
            'avatar_url': 'Enter a URL for your profile picture'
        }

    def clean_avatar_url(self):
        avatar_url = self.cleaned_data.get('avatar_url')
        if avatar_url and not avatar_url.startswith(('http://', 'https://')):
            raise forms.ValidationError('Please enter a valid URL starting with http:// or https://')
        return avatar_url
