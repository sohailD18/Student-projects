from django import forms
from .models import Page, ContentBlock


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'slug', 'parent', 'status', 
                  'meta_title', 'meta_description', 'meta_keywords']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ContentBlockForm(forms.ModelForm):
    class Meta:
        model = ContentBlock
        fields = ['block_type', 'title', 'content', 'order', 
                  'css_classes', 'custom_css', 'is_active']
        widgets = {
            'block_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'css_classes': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_css': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PublishPageForm(forms.Form):
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text='Optional notes about this publish action'
    )
