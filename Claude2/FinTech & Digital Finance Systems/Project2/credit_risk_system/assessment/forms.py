"""
Forms for Credit Risk Assessment System
"""
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .models import Applicant, FinancialData


class ApplicantForm(forms.ModelForm):
    """
    Form for Applicant Financial Profile
    Handles personal and financial information input
    """

    class Meta:
        model = Applicant
        fields = [
            'name', 'email', 'phone', 'annual_income',
            'employment_status', 'years_employed', 'debt_to_income_ratio'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567',
                'required': 'required'
            }),
            'annual_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '50000',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'years_employed': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5',
                'min': '0',
                'max': '50',
                'required': 'required'
            }),
            'debt_to_income_ratio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'required': 'required'
            }),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'annual_income': 'Annual Income ($)',
            'employment_status': 'Employment Status',
            'years_employed': 'Years Employed',
            'debt_to_income_ratio': 'Debt-to-Income Ratio (%)'
        }

    def clean_annual_income(self):
        """Validate annual income is positive"""
        income = self.cleaned_data.get('annual_income')
        if income and income < 0:
            raise ValidationError("Annual income cannot be negative.")
        return income

    def clean_debt_to_income_ratio(self):
        """Validate debt-to-income ratio is within valid range"""
        dti = self.cleaned_data.get('debt_to_income_ratio')
        if dti is not None and (dti < 0 or dti > 100):
            raise ValidationError("Debt-to-income ratio must be between 0 and 100 percent.")
        return dti

    def clean_years_employed(self):
        """Validate years employed is within reasonable range"""
        years = self.cleaned_data.get('years_employed')
        if years is not None and (years < 0 or years > 50):
            raise ValidationError("Years employed must be between 0 and 50.")
        return years


class FinancialDataForm(forms.ModelForm):
    """
    Form for Credit History & Income Data
    Handles credit information input
    """

    class Meta:
        model = FinancialData
        fields = [
            'credit_score', 'num_open_loans', 'num_credit_lines',
            'late_payments', 'bankruptcies', 'home_ownership_status',
            'total_credit_limit', 'credit_utilization'
        ]
        widgets = {
            'credit_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '650',
                'min': '300',
                'max': '850',
                'required': 'required'
            }),
            'num_open_loans': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2',
                'min': '0',
                'required': 'required'
            }),
            'num_credit_lines': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '4',
                'min': '0',
                'required': 'required'
            }),
            'late_payments': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'required': 'required'
            }),
            'bankruptcies': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'home_ownership_status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'total_credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '25000',
                'min': '0',
                'step': '0.01'
            }),
            'credit_utilization': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
        }
        labels = {
            'credit_score': 'Credit Score (300-850)',
            'num_open_loans': 'Number of Open Loans',
            'num_credit_lines': 'Number of Credit Lines',
            'late_payments': 'Late Payments (Last 2 Years)',
            'bankruptcies': 'History of Bankruptcy',
            'home_ownership_status': 'Home Ownership Status',
            'total_credit_limit': 'Total Credit Limit ($)',
            'credit_utilization': 'Credit Utilization (%)'
        }
        help_texts = {
            'credit_score': 'Enter credit score between 300 and 850',
            'num_open_loans': 'Current number of active loans',
            'num_credit_lines': 'Total number of credit lines',
            'late_payments': 'Number of payments 30+ days late in last 2 years',
            'bankruptcies': 'Check if applicant has filed for bankruptcy',
            'home_ownership_status': 'Current housing situation',
            'total_credit_limit': 'Total credit limit across all cards (optional)',
            'credit_utilization': 'Percentage of credit used (optional)'
        }

    def clean_credit_score(self):
        """Validate credit score is within valid range"""
        score = self.cleaned_data.get('credit_score')
        if score and (score < 300 or score > 850):
            raise ValidationError("Credit score must be between 300 and 850.")
        return score

    def clean_num_open_loans(self):
        """Validate number of open loans"""
        loans = self.cleaned_data.get('num_open_loans')
        if loans is not None and loans < 0:
            raise ValidationError("Number of open loans cannot be negative.")
        return loans

    def clean_num_credit_lines(self):
        """Validate number of credit lines"""
        lines = self.cleaned_data.get('num_credit_lines')
        if lines is not None and lines < 0:
            raise ValidationError("Number of credit lines cannot be negative.")
        return lines

    def clean_late_payments(self):
        """Validate late payments count"""
        late = self.cleaned_data.get('late_payments')
        if late is not None and late < 0:
            raise ValidationError("Number of late payments cannot be negative.")
        return late

    def clean_credit_utilization(self):
        """Validate credit utilization is within valid range"""
        utilization = self.cleaned_data.get('credit_utilization')
        if utilization is not None and (utilization < 0 or utilization > 100):
            raise ValidationError("Credit utilization must be between 0 and 100 percent.")
        return utilization


class CombinedAssessmentForm(forms.Form):
    """
    Combined form that includes both Applicant and FinancialData forms
    This allows for a single-page form submission
    """

    # Applicant fields
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter full name'
        }),
        label='Full Name'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
        label='Email Address'
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(555) 123-4567'
        }),
        label='Phone Number'
    )
    annual_income = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '50000',
            'min': '0',
            'step': '0.01'
        }),
        label='Annual Income ($)'
    )
    employment_status = forms.ChoiceField(
        choices=Applicant.EMPLOYMENT_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Employment Status'
    )
    years_employed = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '5',
            'min': '0',
            'max': '50'
        }),
        label='Years Employed'
    )
    debt_to_income_ratio = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '30',
            'min': '0',
            'max': '100',
            'step': '0.01'
        }),
        label='Debt-to-Income Ratio (%)'
    )

    # Financial data fields
    credit_score = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '650',
            'min': '300',
            'max': '850'
        }),
        label='Credit Score (300-850)'
    )
    num_open_loans = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2',
            'min': '0'
        }),
        label='Number of Open Loans',
        initial=0
    )
    num_credit_lines = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '4',
            'min': '0'
        }),
        label='Number of Credit Lines',
        initial=0
    )
    late_payments = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'min': '0'
        }),
        label='Late Payments (Last 2 Years)',
        initial=0
    )
    bankruptcies = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='History of Bankruptcy'
    )
    home_ownership_status = forms.ChoiceField(
        choices=FinancialData.HOME_OWNERSHIP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Home Ownership Status'
    )
    total_credit_limit = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '25000',
            'min': '0',
            'step': '0.01'
        }),
        label='Total Credit Limit ($)'
    )
    credit_utilization = forms.DecimalField(
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '30',
            'min': '0',
            'max': '100',
            'step': '0.01'
        }),
        label='Credit Utilization (%)'
    )

    # Form organization
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add common CSS class to all fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' form-control'
                else:
                    field.widget.attrs['class'] = 'form-control'

    def clean_annual_income(self):
        income = self.cleaned_data.get('annual_income')
        if income and income < 0:
            raise forms.ValidationError("Annual income cannot be negative.")
        return income

    def clean_debt_to_income_ratio(self):
        dti = self.cleaned_data.get('debt_to_income_ratio')
        if dti is not None and (dti < 0 or dti > 100):
            raise forms.ValidationError("Debt-to-income ratio must be between 0 and 100.")
        return dti

    def clean_credit_score(self):
        score = self.cleaned_data.get('credit_score')
        if score and (score < 300 or score > 850):
            raise forms.ValidationError("Credit score must be between 300 and 850.")
        return score
