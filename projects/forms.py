# projects/forms.py
from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nom du projet'}),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea', 'rows': 4}),
        }
