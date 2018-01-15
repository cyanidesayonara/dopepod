from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', )

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('bio', 'location', 'show_explicit', 'dark_theme')
