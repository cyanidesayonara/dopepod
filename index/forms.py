from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from index.models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

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
        fields = ('bio', 'location',)
