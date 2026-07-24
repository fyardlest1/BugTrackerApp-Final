# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model

from .models import Company


class StyledFormMixin:
    """Habille chaque champ avec nos classes Tailwind."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = ('form-select' if isinstance(field.widget, forms.Select) else 'form-input')
            existant = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existant + ' ' + css).strip()


class StyledAuthenticationForm(StyledFormMixin, AuthenticationForm):
    pass


class RegisterForm(StyledFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email')


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(
                attrs={'class': 'form-textarea', 'rows': 4}),
            'logo': forms.ClearableFileInput(attrs={'class': 'block text-sm'}),
        }


class CompanyRegisterForm(RegisterForm):
    company_name = forms.CharField(
        max_length=120, label="Nom de l'entreprise",
        widget=forms.TextInput(attrs={'class': 'form-input'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'avatar': forms.ClearableFileInput(
                attrs={'class': 'block text-sm'}),
        }

"""
Redémarre le serveur. Les libellés, les textes d'aide (help_text) et les erreurs de validation 
(mot de passe trop court, trop courant, uniquement numérique, non-concordance des deux mots de passe) 
s'affichent alors en français, sans rien changer à ta page.
C'est la bonne solution pour tout ce qui est standard. 
Pour les rares messages que tu veux formuler toi-même, tu les surcharges dans le formulaire, pas dans le gabarit. 
Par exemple dans accounts/forms.py :
"""

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': "Nom d'utilisateur",
            'email': 'Adresse email',
        }
        error_messages = {
            'username': {
                'unique': "Ce nom d'utilisateur est déjà pris.",
            },
        }
        

class StyledPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass
