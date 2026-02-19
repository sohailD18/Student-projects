from django import forms
from .models import MediaFile, MediaFolder, MediaCollection


class MediaFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['title', 'description', 'file', 'folder', 'tags', 
                  'alt_text', 'caption', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'folder': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma separated tags'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MediaFolderForm(forms.ModelForm):
    class Meta:
        model = MediaFolder
        fields = ['name', 'slug', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }


class MediaCollectionForm(forms.ModelForm):
    class Meta:
        model = MediaCollection
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Collection Name',
        }
