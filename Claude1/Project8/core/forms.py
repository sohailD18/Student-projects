from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Incident, Comment, UserProfile, IncidentCategory,
    IncidentVerification, Notification, SafetyAlert
)


class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create user profile
            location = self.cleaned_data.get('location', '')
            UserProfile.objects.create(user=user, location=location)
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'location', 'address', 'latitude', 'longitude',
                  'bio', 'profile_picture', 'notification_enabled', 'email_alerts', 'radius_km']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'id': 'location-input'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'id': 'latitude-input'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'id': 'longitude-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 500}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'notification_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'radius_km': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        }


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'location', 'address',
                  'latitude', 'longitude', 'image', 'timestamp', 'severity', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'id': 'incident-location'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional detailed address'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'id': 'incident-latitude'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'id': 'incident-longitude'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'timestamp': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class IncidentSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search incidents...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=IncidentCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Incident.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    severity = forms.ChoiceField(
        choices=[('', 'All Severity')] + Incident.SEVERITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by location...'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...'
            }),
        }


class IncidentVerificationForm(forms.ModelForm):
    class Meta:
        model = IncidentVerification
        fields = ['is_confirmed', 'comments']
        widgets = {
            'is_confirmed': forms.RadioSelect(choices=[
                (True, '✓ This incident is real/accurate'),
                (False, '✗ This appears to be a false report')
            ], attrs={'class': 'form-check-input'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add any additional notes (optional)...'
            }),
        }


class IncidentCategoryForm(forms.ModelForm):
    class Meta:
        model = IncidentCategory
        fields = ['name', 'description', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-exclamation-triangle'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class SafetyAlertForm(forms.ModelForm):
    class Meta:
        model = SafetyAlert
        fields = ['title', 'message', 'severity', 'affected_areas', 'expires_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'affected_areas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Downtown, Westside, North Hills'
            }),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
