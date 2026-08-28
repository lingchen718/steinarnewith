from django import forms
from .models import ArtProject


class ArtProjectForm(forms.ModelForm):
    class Meta:
        model = ArtProject
        fields = ['title', 'description', 'cover_image', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Project title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
        }
        help_texts = {
            'cover_image': 'Shown in the projects list. Falls back to the first Entry if empty.',
            'slug': 'Auto-generated from title if left blank.',
        }
