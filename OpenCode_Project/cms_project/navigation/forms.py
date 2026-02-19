from django import forms
from .models import Navigation, NavigationItem, FooterLink


class NavigationForm(forms.ModelForm):
    class Meta:
        model = Navigation
        fields = ['name', 'slug', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NavigationItemForm(forms.ModelForm):
    class Meta:
        model = NavigationItem
        fields = ['navigation', 'parent', 'title', 'link_type', 'url', 'page', 
                  'target', 'css_classes', 'icon', 'order', 'is_active']
        widgets = {
            'navigation': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'link_type': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'page': forms.Select(attrs={'class': 'form-control'}),
            'target': forms.Select(attrs={'class': 'form-control'}),
            'css_classes': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FooterLinkForm(forms.ModelForm):
    class Meta:
        model = FooterLink
        fields = ['title', 'url', 'group', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
