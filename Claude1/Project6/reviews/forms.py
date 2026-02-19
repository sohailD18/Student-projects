from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }

class StarRatingWidget(forms.RadioSelect):
    template_name = 'reviews/star_rating_widget.html'
    input_type = 'radio'

    def __init__(self, attrs=None, render_value=False):
        choices = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]
        super().__init__(attrs, choices)

class ReviewFormWithStars(forms.ModelForm):
    rating = forms.IntegerField(
        widget=StarRatingWidget,
        initial=5
    )

    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }
