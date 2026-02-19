"""
Forms for AI-Based Intelligent Examination Performance Analysis System
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User, Subject, Topic, Exam, Question,
    StudentAnswer, ExamResult, PerformanceAnalysis
)


class CustomUserCreationForm(UserCreationForm):
    """
    Custom User Registration Form
    Used for both Student and Teacher registration
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (optional)'
        })
    )

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'phone_number', 'date_of_birth', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set password from password1 field
        user.set_password(self.cleaned_data['password1'])
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class SubjectForm(forms.ModelForm):
    """
    Form for creating/editing Subjects
    """
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mathematics'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MATH101'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the subject'
            })
        }


class TopicForm(forms.ModelForm):
    """
    Form for creating/editing Topics
    """
    class Meta:
        model = Topic
        fields = ['subject', 'name', 'description', 'chapter_number']
        widgets = {
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Algebra'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Topic description'
            }),
            'chapter_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            })
        }


class ExamForm(forms.ModelForm):
    """
    Form for creating/editing Exams
    """
    class Meta:
        model = Exam
        fields = ['title', 'subject', 'description', 'total_marks',
                  'duration_minutes', 'passing_marks', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mid-Term Mathematics Exam'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Exam instructions and description'
            }),
            'total_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'e.g., 100'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'e.g., 60'
            }),
            'passing_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'e.g., 40'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }


class QuestionForm(forms.ModelForm):
    """
    Form for creating/editing Questions
    """
    class Meta:
        model = Question
        fields = ['exam', 'topic', 'question_type', 'text', 'option_a', 'option_b',
                  'option_c', 'option_d', 'correct_answer', 'marks', 'question_number', 'explanation']
        widgets = {
            'exam': forms.Select(attrs={
                'class': 'form-control'
            }),
            'topic': forms.Select(attrs={
                'class': 'form-control'
            }),
            'question_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your question here...'
            }),
            'option_a': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option A'
            }),
            'option_b': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option B'
            }),
            'option_c': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option C (optional)'
            }),
            'option_d': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option D (optional)'
            }),
            'correct_answer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.5,
                'step': 0.5,
                'placeholder': 'e.g., 2'
            }),
            'question_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Question order'
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explain why this is the correct answer (optional)'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make option fields not required for True/False questions
        self.fields['option_a'].required = False
        self.fields['option_b'].required = False
        self.fields['option_c'].required = False
        self.fields['option_d'].required = False
        # Make exam field not required (we set it manually in the view)
        self.fields['exam'].required = False


class TakeExamForm(forms.Form):
    """
    Dynamic form for taking exams
    Form fields are generated based on exam questions
    """
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', None)
        super().__init__(*args, **kwargs)

        if questions:
            for question in questions:
                field_name = f'question_{question.id}'
                choices = []

                if question.question_type == 'mcq':
                    choices = [
                        ('A', question.option_a),
                        ('B', question.option_b),
                    ]
                    if question.option_c:
                        choices.append(('C', question.option_c))
                    if question.option_d:
                        choices.append(('D', question.option_d))
                elif question.question_type == 'true_false':
                    choices = [
                        ('True', 'True'),
                        ('False', 'False'),
                    ]

                self.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.RadioSelect(attrs={
                        'class': 'form-check-input'
                    }),
                    required=True,
                    label=f"Q{question.question_number}. {question.text}"
                )


class LoginForm(forms.Form):
    """
    Custom Login Form
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class DateRangeFilterForm(forms.Form):
    """
    Form for filtering performance analysis by date range
    """
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class SubjectFilterForm(forms.Form):
    """
    Form for filtering by subject
    """
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        empty_label="All Subjects",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
