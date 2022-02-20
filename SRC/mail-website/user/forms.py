# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
#
# from .models import CustomUser
#
#
# class CustomUserCreationForm(UserCreationForm):
#     class Meta(UserCreationForm):
#         model = CustomUser
#         fields = ('email',)
#
#
# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = CustomUser
#         fields = ('email',)
#
from django import forms
from user.models import Users
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)

    class Meta:
        model = Users
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
#
#
# class SignupForm(UserCreationForm):
#     email = forms.EmailField(max_length=200, help_text='Required')
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2')