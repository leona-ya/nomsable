import datetime
import json
import random

import requests
from bs4 import BeautifulSoup
from django.http import Http404
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import redirect
from pint import UnitRegistry

from accounts.helper import LoginRequiredMixin
from core.forms import ParserInsertForm
from django.forms import ModelForm
from core.models import Recipe, RecipeIngredient, RecipeInstruction, Ingredient

import isodate

class IndexView(LoginRequiredMixin, TemplateView):

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # to be replaced by actual function
        recipes = Recipe.objects.all()
        context["cook_next_recipes"] = random.sample(list(recipes), min(5, recipes.count()))

        context["latest_recipes"] = Recipe.objects.all().order_by("-date_created")[:5]
        return context


def parse_iso8601_duration(iso_duration):
    if iso_duration is not None:
        maybe_timedelta = isodate.parse_duration(iso_duration)
        if isinstance(maybe_timedelta, datetime.timedelta):
            iso_duration = maybe_timedelta
    return iso_duration

def parse_ingredient(unit_registry, recipe, raw_ingredient):
    ingredient_parts = raw_ingredient.split(" ")
    quantity = None
    last_parseable_idx = 0
    for idx, _ in enumerate(ingredient_parts, start=1):
        try:
            quantity = unit_registry(" ".join(ingredient_parts[:idx]))
        except Exception as e:
            break
        last_parseable_idx = idx

    ingredient_part_str = " ".join(ingredient_parts[(last_parseable_idx + 1):])
    comma_position = ingredient_part_str.find(",")
    if comma_position > 0:
        ingredient = ingredient_part_str[:comma_position]
        description = ingredient_part_str[comma_position + 1:]
    else:
        ingredient = ingredient_part_str
        description = None

    try:
        ingredient_obj = Ingredient.objects.get(name=ingredient)
    except Ingredient.DoesNotExist:
        ingredient_obj = Ingredient(name=ingredient)
        ingredient_obj.save()

    return RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=ingredient_obj.id,
        unit=unit_registry.get_symbol(str(quantity.u)) if hasattr(quantity, "u") else None,
        quantity=quantity.m if hasattr(quantity, "m") else None,
        description=description
    )


class ParserInsertView(LoginRequiredMixin, View):
    template_name = "core/new.html"

    def get(self, request):
        parser_insert_form = ParserInsertForm()
        return render(request, self.template_name, {
            "form": parser_insert_form
        })

    def post(self, request):
        parser_insert_form = ParserInsertForm(request.POST)
        if not parser_insert_form.is_valid():
            return render(request, "core/new.html", {
                "form": parser_insert_form
            })  # add form errors
        requested_url = parser_insert_form.cleaned_data["url"]
        request = requests.get(requested_url)
        parsed_html = BeautifulSoup(request.text, features="html.parser")
        ld_json = json.loads(
            parsed_html.find("script", attrs={"type": "application/ld+json"}).text)  # check if @type is Recipe
        recipe = Recipe(
            name=ld_json["name"],
            description=ld_json["description"],
            image=ld_json.get("image"),
            prep_time=parse_iso8601_duration(ld_json.get("prepTime")),
            cook_time=parse_iso8601_duration(ld_json.get("cookTime")),
            total_time=parse_iso8601_duration(ld_json.get("totalTime")),
            author=", ".join([author["name"] for author in ld_json["author"]]) if type(ld_json["author"]) == list else ld_json["author"]["name"],
            keywords=ld_json["keywords"].split(", "),
            publisher=ld_json["publisher"]["name"],
            publisher_url=ld_json["publisher"].get("requested_url"),
            origin_url=requested_url,
            added_by=self.request.user
        )
        recipe.save()
        unit_registry = UnitRegistry()
        ingredients = [parse_ingredient(unit_registry, recipe, raw_ingredient) for raw_ingredient in ld_json["recipeIngredient"]]
        RecipeIngredient.objects.bulk_create(ingredients)

        instructions = [RecipeInstruction(
            recipe=recipe,
            step_no=idx,
            text=ld_json_instruction["text"]
        ) for idx, ld_json_instruction in enumerate(ld_json["recipeInstructions"], start=1)]
        RecipeInstruction.objects.bulk_create(instructions)
        return redirect("core:index")

class RecipeView(TemplateView):
    template_name = "core/recipe.html"

    def get_context_data(self, recipe_id, **kwargs):
        context = super().get_context_data(**kwargs)
        # to be replaced by actual function
        try:
            context["recipe"] = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            raise Http404

        return context

class EditView(TemplateView):
    template_name = "core/edit.html"

    def get_context_data(self, recipe_id, **kwargs):
        context = super().get_context_data(**kwargs)
        # to be replaced by actual function
        try:
            context["recipe"] = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            raise Http404

        return context


def error_404_view(request, exception):
    return render(request, 'core/404.html')