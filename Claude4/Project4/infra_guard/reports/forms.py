"""
Forms for InfraGuard Application
"""

from django import forms
from django.contrib.auth.models import User
from .models import Incident, Claim, UserProfile


class UserRegistrationForm(forms.ModelForm):
    """Registration form for new users"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        label='Confirm Password'
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='I am a',
        initial='citizen'
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional phone number'
        }),
        required=False,
        label='Phone Number'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered!")
        return email


class IncidentReportForm(forms.ModelForm):
    """Form for reporting infrastructure incidents"""
    incident_type = forms.ChoiceField(
        choices=Incident.INCIDENT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'incident_type'
        }),
        label='Incident Type',
        help_text='Auto-detected by AI, but you can override'
    )

    class Meta:
        model = Incident
        fields = ['location', 'description', 'incident_type', 'image', 'latitude', 'longitude']
        widgets = {
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter street address or landmark',
                'id': 'location'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the incident in detail (what, where, severity)',
                'rows': 4,
                'id': 'description'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'latitude': forms.HiddenInput(attrs={'id': 'latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'longitude'}),
        }
        labels = {
            'location': 'Location',
            'description': 'Description',
            'image': 'Upload Image (Optional)'
        }


class ClaimForm(forms.ModelForm):
    """Form for filing compensation claims"""

    class Meta:
        model = Claim
        fields = ['victim_name', 'claim_amount', 'evidence_description']
        widgets = {
            'victim_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of the victim/claimant'
            }),
            'claim_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount in local currency',
                'step': '0.01',
                'min': '0'
            }),
            'evidence_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Provide detailed evidence and justification for the claim amount',
                'rows': 5
            }),
        }
        labels = {
            'victim_name': 'Victim/Claimant Name',
            'claim_amount': 'Claim Amount',
            'evidence_description': 'Evidence Description'
        }


class IncidentVerificationForm(forms.Form):
    """Form for authorities to verify/reject incidents"""
    action = forms.ChoiceField(
        choices=[
            ('verify', 'Verify Incident'),
            ('reject', 'Reject Incident'),
            ('resolve', 'Mark as Resolved')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add notes explaining your decision (optional)'
        }),
        required=False,
        label='Authority Notes'
    )


class ClaimReviewForm(forms.Form):
    """Form for authorities to review claims"""
    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approve Claim'),
            ('reject', 'Reject Claim')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    approved_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave same as claimed if approving full amount',
            'step': '0.01',
            'min': '0'
        }),
        required=False,
        label='Approved Amount'
    )
    review_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add notes explaining your decision'
        }),
        label='Review Notes'
    )
