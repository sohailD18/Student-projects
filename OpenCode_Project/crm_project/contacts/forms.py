"""
Forms for CRM Contacts app
"""

from django import forms
from .models import Company, Contact


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'logo', 'industry', 'company_size', 'website', 'email', 'phone',
            'address', 'city', 'state', 'country', 'linkedin', 'twitter', 'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'company', 'salutation', 'first_name', 'last_name', 'email', 'phone',
            'mobile', 'job_title', 'department', 'status', 'source', 'address',
            'city', 'state', 'country', 'postal_code', 'linkedin', 'twitter', 'notes', 'tags'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
