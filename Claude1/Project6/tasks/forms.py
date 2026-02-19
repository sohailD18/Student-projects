from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'required_skills', 'estimated_duration')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'required_skills': forms.TextInput(
                attrs={'placeholder': 'e.g., gardening, cooking, plumbing'}
            ),
        }
        help_texts = {
            'required_skills': 'Enter skills separated by commas'
        }

class TaskSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by skill...',
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All')] + Task.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
