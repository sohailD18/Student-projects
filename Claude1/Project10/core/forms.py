from django import forms
from .models import Skill, Session, Review


class SkillForm(forms.ModelForm):
    """Form for creating a new skill listing"""
    class Meta:
        model = Skill
        fields = ['title', 'description', 'category', 'hourly_rate_points']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Introduction to Python Programming'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe what you will teach, prerequisites, and learning outcomes...'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'hourly_rate_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Points required per session'
            })
        }
        labels = {
            'hourly_rate_points': 'Points Per Session'
        }
        help_texts = {
            'hourly_rate_points': 'How many points students need to spend for one session with you'
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['scheduled_time']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            })
        }
        help_texts = {
            'scheduled_time': 'Select when you would like to schedule this session'
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience (optional)...'
            })
        }
        labels = {
            'rating': 'How was your session?',
            'comment': 'Review Comment'
        }