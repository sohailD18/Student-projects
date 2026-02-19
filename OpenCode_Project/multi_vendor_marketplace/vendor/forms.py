"""
Forms for Multi-Vendor Marketplace
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Vendor, Product, Review


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def save(self, commit=True):
        user = super().save(commit=True)
        return user


class VendorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'store_name', 'store_slug', 'description', 'logo', 'banner',
            'contact_email', 'contact_phone', 'address',
            'bank_name', 'bank_account_number', 'bank_routing_number', 'paypal_email'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'slug', 'description', 'price', 'sale_price',
            'stock_quantity', 'sku', 'image', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
