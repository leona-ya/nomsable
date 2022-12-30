from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import UUIDField

from accounts.models import User, InviteCode


class AuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label="Username or Email", widget=forms.TextInput(attrs={"autofocus": True})
    )


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('invite_code', 'username', 'name', 'email', 'password1', 'password2', )

    invite_code = UUIDField(
        label="Invite code"
    )

    def clean_invite_code(self):
        invite_code = self.cleaned_data['invite_code']
        if not InviteCode.is_code_valid(invite_code):
            raise ValidationError("Invite code not valid")
        return invite_code

    def save(self):
        InviteCode.objects.get(code=self.cleaned_data["invite_code"]).delete()
        return super().save()
