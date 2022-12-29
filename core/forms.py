from django import forms
from django.forms import ModelForm
from core.models import Recipe, RecipeIngredient, RecipeInstruction
from django.forms import formset_factory, modelformset_factory

class ParserInsertForm(forms.Form):
    url = forms.URLField(label="website url")

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'prep_time', 'cook_time', 'total_time', 'tags']

IngredientFormSet = modelformset_factory(
    RecipeIngredient,
    fields=('ingredient', 'unit', 'quantity', 'description'),
)

InstructionFormSet = modelformset_factory(
    RecipeInstruction,
    fields=('step_no', 'text'),
)
