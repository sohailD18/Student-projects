"""
Django Forms for FinRisk AI
"""
from django import forms
from .models import UserProfile, Transaction


class UserProfileForm(forms.ModelForm):
    """
    Form for creating and updating UserProfile
    Module 1: Financial Behavior Data Collection
    """
    class Meta:
        model = UserProfile
        fields = [
            'name', 'age', 'annual_income', 'employment_status',
            'income_stability', 'dependents', 'investment_experience_years'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '18',
                'placeholder': 'Age'
            }),
            'annual_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Annual Income'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'income_stability': forms.Select(attrs={
                'class': 'form-select'
            }),
            'dependents': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'value': '0'
            }),
            'investment_experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'value': '0'
            }),
        }


class TransactionForm(forms.ModelForm):
    """
    Form for creating and updating Transactions
    Module 1: Financial Behavior Data Collection
    """
    class Meta:
        model = Transaction
        fields = ['date', 'category', 'amount', 'transaction_type', 'description']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Amount'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional description'
            }),
        }


class QuickTransactionForm(forms.ModelForm):
    """
    Quick form for adding transactions with default values
    """
    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'transaction_type']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Amount'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
