from django import forms
from .models import Job, JobApplication


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'category', 'job_type',
            'experience_level', 'description', 'requirements',
            'salary_min', 'salary_max', 'is_salary_visible',
            'application_deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Senior Software Engineer'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Tech Corp'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. San Francisco, CA'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe the role and responsibilities...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'List the requirements and qualifications...'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum salary',
                'step': '1000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum salary',
                'step': '1000'
            }),
            'is_salary_visible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'cover_letter', 'resume', 'phone', 'linkedin_profile',
            'portfolio_url', 'expected_salary'
        ]
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Tell us why you\'re interested in this role...'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. +1 234 567 8900'
            }),
            'linkedin_profile': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourportfolio.com'
            }),
            'expected_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your expected salary',
                'step': '1000'
            }),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Check file size (max 5MB)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Resume file size cannot exceed 5MB.')

            # Check file extension
            valid_extensions = ['.pdf', '.doc', '.docx']
            import os
            ext = os.path.splitext(resume.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Only PDF and Word documents are allowed.')

        return resume
