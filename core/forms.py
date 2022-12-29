from django import forms
from core.models import Ingredient, Recipe, RecipeIngredient, RecipeInstruction
from django.forms import ModelForm, formset_factory, modelformset_factory, widgets
from django.core.exceptions import ValidationError

class ParserInsertForm(forms.Form):
    url = forms.URLField(label="website url")

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'prep_time', 'cook_time', 'total_time', 'tags']

class IngredientForm(ModelForm):
    ingredient = forms.CharField()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get("ingredient") is not None:
           self.initial["ingredient"] = Ingredient.objects.get(pk=self.initial["ingredient"]).name

    def clean_ingredient(self):
        try:
            ingredient = self.cleaned_data['ingredient']
        except AttributeError:
            raise ValidationError("Couldn't find ingredient uwu")
        obj, _ = Ingredient.objects.get_or_create(name=ingredient)
        return obj

IngredientFormSet = modelformset_factory(
    RecipeIngredient,
    fields = ('ingredient', 'unit', 'quantity', 'description'),
    form=IngredientForm,
)

InstructionFormSet = modelformset_factory(
    RecipeInstruction,
    fields=('step_no', 'text'),
)
