from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from typing import TYPE_CHECKING, cast, Any

if TYPE_CHECKING:
    class UserCreationFormMeta:
        model: Any
        fields: list[str]

class UserRegisterForm(UserCreationForm):
    """Form for user registration with extended fields."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=30)

    class Meta:
        if TYPE_CHECKING:
            _parent = cast('UserCreationFormMeta', UserCreationForm)
        else:
            _parent = UserCreationForm.Meta

        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']



class UserUpdateForm(forms.ModelForm):
    """Form for updating user information."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


class ProfileUpdateForm(forms.Form):
    """Form for updating profile information."""
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    location = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'


class CustomAuthForm(AuthenticationForm):
    """Form for user authentication with Bootstrap styling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
