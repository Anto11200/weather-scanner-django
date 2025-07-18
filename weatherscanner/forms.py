# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.models import User
# from django import forms
# from django.forms.widgets import PasswordInput, TextInput

# # - Creazione dell'utente

# class CreateUserForm(UserCreationForm):
    
#     class Meta:
        
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']

        
# # - Autenticazione dell'utente

# class LoginForm(AuthenticationForm):
    
#     username = forms.CharField(widget=TextInput())
#     password = forms.CharField(widget=PasswordInput())
