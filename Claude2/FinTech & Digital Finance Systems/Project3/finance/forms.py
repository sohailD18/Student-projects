"""
Django Forms for the Finance Platform.
"""
import calendar

from django import forms
from .models import Transaction, Budget, Category


class TransactionForm(forms.ModelForm):
    """
    Form for adding and editing transactions.
    """
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'transaction_type', 'category', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount',
                'step': '0.01',
                'min': '0.01'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Grocery shopping at Walmart'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty choice for category
        self.fields['category'].empty_label = "Select a category"

    def clean_description(self):
        """Auto-suggest category based on description if not provided."""
        description = self.cleaned_data.get('description', '')

        if description and not self.cleaned_data.get('category') or self.cleaned_data.get('category') == Category.OTHER:
            from .services import CategoryClassifier
            suggested = CategoryClassifier.suggest_category(description)

            # Only auto-set if user hasn't explicitly selected OTHER
            if self.data.get('category') != Category.OTHER:
                self.cleaned_data['category'] = suggested

        return description


class BudgetForm(forms.ModelForm):
    """
    Form for creating and editing budgets.
    """
    class Meta:
        model = Budget
        fields = ['category', 'limit_amount', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'limit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter budget limit',
                'step': '0.01',
                'min': '1'
            }),
            'month': forms.Select(attrs={
                'class': 'form-control'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2030'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"

        # Set default month and year to current
        from django.utils import timezone
        today = timezone.now().date()
        self.fields['month'].initial = today.month
        self.fields['year'].initial = today.year


class TransactionBulkImportForm(forms.Form):
    """
    Form for bulk importing transactions via CSV.
    """
    csv_file = forms.FileField(
        label='CSV File',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )


class ReportFilterForm(forms.Form):
    """
    Form for filtering reports by month and year.
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year = forms.ChoiceField(
        choices=[(y, y) for y in range(2020, 2031)],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        today = timezone.now().date()
        self.fields['month'].initial = today.month
        self.fields['year'].initial = today.year
