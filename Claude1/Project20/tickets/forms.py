from django import forms
from .models import Complaint, Ticket, Feedback


class ComplaintForm(forms.ModelForm):
    """Form for users to submit complaints/issues."""

    class Meta:
        model = Complaint
        fields = ['name', 'email', 'category', 'priority', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Please describe your issue in detail...'
            }),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'category': 'Issue Category',
            'priority': 'Priority Level',
            'description': 'Description',
        }
        help_texts = {
            'category': 'Select the category that best describes your issue',
            'priority': 'How urgent is this issue?',
        }

    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email

    def clean_description(self):
        """Ensure description has meaningful content."""
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise forms.ValidationError('Please provide more details (at least 10 characters).')
        return description.strip()


class TicketUpdateForm(forms.ModelForm):
    """Form for staff to update ticket status and assignment."""

    class Meta:
        model = Ticket
        fields = ['status', 'assigned_staff']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assigned_staff': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter staff member name'
            }),
        }
        labels = {
            'status': 'Ticket Status',
            'assigned_staff': 'Assigned Staff Member',
        }
        help_texts = {
            'status': 'Update the current status of this ticket',
            'assigned_staff': 'Assign this ticket to a staff member',
        }

    def clean_assigned_staff(self):
        """Validate and format staff name."""
        staff = self.cleaned_data.get('assigned_staff')
        if staff:
            staff = staff.strip().title()
        return staff


class FeedbackForm(forms.ModelForm):
    """Form for customers to submit feedback on closed tickets."""

    rating = forms.ChoiceField(
        choices=[(i, f'{"⭐" * i} - {["Poor", "Fair", "Good", "Very Good", "Excellent"][i-1]}') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='How would you rate your experience?'
    )

    class Meta:
        model = Feedback
        fields = ['rating', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us more about your experience (optional)...'
            }),
        }
        labels = {
            'comments': 'Additional Comments',
        }

    def clean_rating(self):
        """Validate rating is between 1 and 5."""
        rating = self.cleaned_data.get('rating')
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise forms.ValidationError('Rating must be between 1 and 5.')
        except (ValueError, TypeError):
            raise forms.ValidationError('Please select a valid rating.')
        return rating
