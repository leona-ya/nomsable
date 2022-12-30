from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class AuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label="Username or Email", widget=forms.TextInput(attrs={"autofocus": True})
    )
