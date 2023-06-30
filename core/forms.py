from django import forms
from django.core.exceptions import ValidationError
from django.forms import (
    ModelForm,
    formset_factory,
    inlineformset_factory,
    modelformset_factory,
    widgets,
)

from core.models import Ingredient, Recipe, RecipeIngredient, RecipeInstruction, Tag


class ParserInsertForm(forms.Form):
    url = forms.URLField(label="website url")


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "name",
            "description",
            "prep_time",
            "cook_time",
            "total_time",
            "image",
            "author",
            "origin_url",
            "publisher",
            "publisher_url",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "style": "line-height: 1.2; font-size: 3.2rem; margin-top: 0.46rem; height: 4.6rem;"
                }
            ),
            "description": forms.Textarea(attrs={"style": "height: inherit;"}),
        }


class IngredientForm(ModelForm):
    # recipe_id = forms.CharField()
    ingredient = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get("ingredient") is not None:
            self.initial["ingredient"] = Ingredient.objects.get(
                pk=self.initial["ingredient"]
            ).name

    def clean_ingredient(self):
        try:
            ingredient = self.cleaned_data["ingredient"]
        except AttributeError:
            raise ValidationError("Couldn't find ingredient uwu")
        obj, _ = Ingredient.objects.get_or_create(name=ingredient)
        return obj


class SearchForm(forms.Form):
    search = forms.CharField(
        label="search", widget=forms.TextInput(attrs={"placeholder": "search"})
    )


IngredientFormSet = modelformset_factory(
    RecipeIngredient,
    fields=("ingredient", "quantity", "description"),
    form=IngredientForm,
    widgets={
        "quantity": forms.TextInput(),
    },
    can_delete=True,
)

InstructionFormSet = modelformset_factory(
    RecipeInstruction,
    fields=("step_no", "text"),
    can_delete=True,
)


class RecipeTagForm(forms.ModelForm):
    tag = forms.CharField(label="Tags")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get("tag") is not None:
            self.initial["tag"] = Tag.objects.get(pk=self.initial["tag"]).name

    def clean_tag(self):
        tag, _ = Tag.objects.get_or_create(name=self.cleaned_data["tag"])
        return tag


RecipeTagFormSet = inlineformset_factory(
    Recipe,
    Recipe.tags.through,
    fields=("tag",),
    form=RecipeTagForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True,
)
