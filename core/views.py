import datetime
import json
import operator
import random
import re
from functools import reduce

import isodate
import requests
from bs4 import BeautifulSoup
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView
from pint import UnitRegistry

from accounts.helper import LoginRequiredMixin
from core.forms import (
    IngredientFormSet,
    InstructionFormSet,
    ParserInsertForm,
    RecipeForm,
    RecipeTagFormSet,
    SearchForm,
)
from core.models import Ingredient, Recipe, RecipeIngredient, RecipeInstruction


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipes = Recipe.objects.all()
        context["cook_next_recipes"] = random.sample(
            list(recipes), min(5, recipes.count())
        )
        context["greeting"] = random.choice(
            [
                "welcome back",
                "welcome",
                "willkommen",
                "bonjour",
                "salut!",
                "hey",
                "hi",
                "hello",
                "howdy",
                "mew",
                "heyyy",
                "hiya",
                "kama pona",
                "pona!",
                "o!",
                "greetings",
                "你好",
                "long-time no see",
                "sup",
                "good to see you",
                "hoi",
                "¡hola",
                "¡hi",
                "servus",
                "gude",
            ]
        )
        context["greeting_emoji"] = random.choices(
            population=[
                "",
                ":3",
                "🐈",
                "=^-^=",
                ":3~",
                "⁼^⁻^⁼",
                "purr~",
            ],
            weights=[
                0.2,
                0.4,
                0.1,
                0.1,
                0.1,
                0.05,
                0.05,
            ],
            k=1,
        )[0]
        context["search_form"] = SearchForm()
        context["latest_recipes"] = Recipe.objects.all().order_by("-date_created")[:5]
        return context


class SearchView(LoginRequiredMixin, View):
    template_name = "core/search.html"

    def get(self, request):
        return render(request, self.template_name, {"search_form": SearchForm})

    def post(self, request):
        query = SearchForm(request.POST)
        if not query.is_valid():
            return render(
                request, "core/search.html", {"search_form": SearchForm}
            )  # add form errors
        search_term = re.split(" |,", query.cleaned_data["search"].lower())

        ingredient_term = []
        for idx, term in enumerate(search_term):
            if term.startswith("ingredient:"):
                ingredient_term.append(search_term.pop(idx)[11:])

        user_term = []
        for idx, term in enumerate(search_term):
            if term.startswith("added_by:"):
                user_term.append(search_term.pop(idx)[9:])

        wildcard = False
        for idx, term in enumerate(search_term):
            if term.startswith("*"):
                wildcard = True

        if wildcard:
            search_results = Recipe.objects.all()
        else:
            search_results = Recipe.objects.filter(
                reduce(
                    operator.and_,
                    (
                        Q(name__contains=x) | Q(description__contains=x)
                        for x in search_term
                    ),
                    ~Q(pk__in=[]),
                ),
                reduce(
                    operator.and_,
                    (
                        Q(ingredients__ingredient__name__contains=x)
                        | Q(ingredients__description__contains=x)
                        for x in ingredient_term
                    ),
                    ~Q(pk__in=[]),
                ),
                reduce(
                    operator.and_,
                    (Q(added_by__username=x) for x in user_term),
                    ~Q(pk__in=[]),
                ),
            )
        """| Q(keywords__contains=[x])"""
        return render(
            request,
            self.template_name,
            {"search_form": query, "search_results": search_results},
        )


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
        except:
            break
        last_parseable_idx = idx

    ingredient_part_str = " ".join(ingredient_parts[(last_parseable_idx + 1) :])
    comma_position = ingredient_part_str.find(",")
    if comma_position > 0:
        ingredient = ingredient_part_str[:comma_position]
        description = ingredient_part_str[comma_position + 1 :]
    else:
        ingredient = ingredient_part_str
        description = None

    try:
        ingredient_obj = Ingredient.objects.get(name=ingredient)
    except Ingredient.DoesNotExist:
        ingredient_obj = Ingredient(name=ingredient)
        ingredient_obj.save()

    unit = None
    try:
        unit = (
            unit_registry.get_symbol(str(quantity.u))
            if hasattr(quantity, "u")
            else None
        )
    except:
        pass

    return RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=ingredient_obj.id,
        unit=unit,
        quantity=quantity.m if hasattr(quantity, "m") else None,
        description=description,
    )


class ParserInsertView(LoginRequiredMixin, View):
    template_name = "core/new.html"

    def get(self, request):
        parser_insert_form = ParserInsertForm()
        return render(request, self.template_name, {"form": parser_insert_form})

    def post(self, request):
        parser_insert_form = ParserInsertForm(request.POST)
        if not parser_insert_form.is_valid():
            return render(
                request, "core/new.html", {"form": parser_insert_form}
            )  # add form errors
        requested_url = parser_insert_form.cleaned_data["url"]
        request = requests.get(requested_url)
        parsed_html = BeautifulSoup(request.text, features="html.parser")
        ld_json = json.loads(
            parsed_html.find("script", attrs={"type": "application/ld+json"}).text
        )  # check if @type is Recipe
        recipe = Recipe(
            name=ld_json["name"],
            description=ld_json["description"],
            image=ld_json.get("image"),
            prep_time=parse_iso8601_duration(ld_json.get("prepTime")),
            cook_time=parse_iso8601_duration(ld_json.get("cookTime")),
            total_time=parse_iso8601_duration(ld_json.get("totalTime")),
            author=", ".join([author["name"] for author in ld_json["author"]])
            if type(ld_json["author"]) == list
            else ld_json["author"]["name"],
            keywords=ld_json["keywords"].split(", "),
            publisher=ld_json["publisher"]["name"],
            publisher_url=ld_json["publisher"].get("requested_url"),
            origin_url=requested_url,
            added_by=self.request.user,
        )
        recipe.save()
        unit_registry = UnitRegistry()
        ingredients = [
            parse_ingredient(unit_registry, recipe, raw_ingredient)
            for raw_ingredient in ld_json["recipeIngredient"]
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

        instructions = [
            RecipeInstruction(
                recipe=recipe, step_no=idx, text=ld_json_instruction["text"]
            )
            for idx, ld_json_instruction in enumerate(
                ld_json["recipeInstructions"], start=1
            )
        ]
        RecipeInstruction.objects.bulk_create(instructions)
        return redirect("core:edit", recipe_id=recipe.id)


class RecipeView(TemplateView):
    template_name = "core/recipe.html"

    def get_context_data(self, recipe_id, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["recipe"] = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            raise Http404
        return context


class EditView(View):
    def get(self, request, recipe_id):
        recipe = Recipe.objects.get(pk=recipe_id)
        recipe_form = RecipeForm(instance=recipe)
        recipe_tag_form = RecipeTagFormSet(prefix="recipe_tag", instance=recipe)
        ingredient_form = IngredientFormSet(
            prefix="ingredients",
            queryset=Recipe.objects.get(pk=recipe_id).ingredients.all(),
        )
        instruction_form = InstructionFormSet(
            prefix="steps", queryset=Recipe.objects.get(pk=recipe_id).instructions.all()
        )
        return render(
            request,
            "core/edit.html",
            {
                "recipe_form": recipe_form,
                "recipe_tag_form": recipe_tag_form,
                "ingredient_form": ingredient_form,
                "instruction_form": instruction_form,
            },
        )

    def post(self, request, recipe_id):
        recipe = Recipe.objects.get(pk=recipe_id)
        recipe_form = RecipeForm(request.POST, instance=recipe)
        recipe_tag_form = RecipeTagFormSet(
            request.POST, prefix="recipe_tag", instance=recipe
        )
        ingredient_form = IngredientFormSet(request.POST, prefix="ingredients")
        instruction_form = InstructionFormSet(request.POST, prefix="steps")
        if (
            recipe_form.is_valid()
            and recipe_tag_form.is_valid()
            and ingredient_form.is_valid()
            and instruction_form.is_valid()
        ):
            # todo: Actually validate
            recipe_form.save()
            recipe_tag_form.save()
            ingredient_form.save(commit=False)
            ingredient_form.save_existing_objects()
            ingredient_form.save_new_objects(commit=False)
            for new_ingredient in ingredient_form.new_objects:
                new_ingredient.recipe_id = recipe_id
                new_ingredient.save()
            instruction_form.save(commit=False)
            instruction_form.save_existing_objects()
            instruction_form.save_new_objects(commit=False)
            for new_instruction in instruction_form.new_objects:
                new_instruction.recipe_id = recipe_id
                new_instruction.save()
            return redirect("core:detail", recipe_id=recipe_id)
        return render(
            request,
            "core/edit.html",
            {
                "recipe_form": recipe_form,
                "recipe_tag_form": recipe_tag_form,
                "ingredient_form": ingredient_form,
                "instruction_form": instruction_form,
            },
        )


def error_404_view(request, exception):
    return render(request, "core/404.html")


class AboutView(TemplateView):
    template_name = "core/about.html"
