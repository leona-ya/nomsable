from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UsernameField,
)
from django.core.exceptions import ValidationError
from django.forms import ModelMultipleChoiceField, UUIDField

from accounts.models import InviteCode, User, UserPreferences


class AuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label="Username or Email", widget=forms.TextInput(attrs={"autofocus": True})
    )


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "invite_code",
            "username",
            "name",
            "email",
            "password1",
            "password2",
        )

    invite_code = UUIDField(label="Invite code")

    def clean_invite_code(self):
        invite_code = self.cleaned_data["invite_code"]
        if not InviteCode.is_code_valid(invite_code):
            raise ValidationError("Invite code not valid")
        return invite_code

    def save(self):
        InviteCode.objects.get(code=self.cleaned_data["invite_code"]).delete()
        return super().save()


class NameFieldModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class RecipeFilterForm(forms.ModelForm):
    from core.models import Ingredient, Tag

    class Meta:
        model = UserPreferences
        fields = ["hidden_recipe_tags", "hidden_recipe_ingredients"]

    hidden_recipe_tags = NameFieldModelMultipleChoiceField(
        queryset=Tag.objects.all(), label="with tag"
    )
    hidden_recipe_ingredients = NameFieldModelMultipleChoiceField(
        queryset=Ingredient.objects.all(), label="with ingredient"
    )
