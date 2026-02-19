from django import forms
from .models import EmailList, Subscriber, EmailTemplate, Campaign


class EmailListForm(forms.ModelForm):
    class Meta:
        model = EmailList
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'List name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email', 'first_name', 'last_name', 'email_list', 'status']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email_list': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class BulkImportSubscribersForm(forms.Form):
    csv_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Paste CSV data here (email, first_name, last_name)...'
        }),
        help_text='Format: email, first_name, last_name (one per line)'
    )
    email_list = forms.ModelChoiceField(
        queryset=EmailList.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select Email List'
    )


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'html_content', 'text_content', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Template name'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email subject'}),
            'html_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'id': 'html_editor'}),
            'text_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'email_template', 'email_list', 'scheduled_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campaign name'}),
            'email_template': forms.Select(attrs={'class': 'form-control'}),
            'email_list': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class ABTestCampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'email_list', 'ab_test_variant_a', 'ab_test_variant_b',
                  'ab_test_split_percentage', 'scheduled_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campaign name'}),
            'email_list': forms.Select(attrs={'class': 'form-control'}),
            'ab_test_variant_a': forms.Select(attrs={'class': 'form-control'}),
            'ab_test_variant_b': forms.Select(attrs={'class': 'form-control'}),
            'ab_test_split_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'value': 50
            }),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
