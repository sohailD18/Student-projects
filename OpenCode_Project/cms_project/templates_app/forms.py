from django import forms
from .models import Template, Theme


class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['name', 'slug', 'description', 'template_type', 'thumbnail', 
                  'is_default', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ['name', 'slug', 'description', 'primary_color', 'secondary_color', 
                  'accent_color', 'background_color', 'text_color', 'font_family', 
                  'font_size_base', 'custom_css', 'custom_js', 'is_default', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'font_family': forms.Select(attrs={'class': 'form-control'}),
            'font_size_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'custom_css': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'custom_js': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
