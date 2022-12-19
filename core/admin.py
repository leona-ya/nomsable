from django.contrib import admin

from core.models import Recipe, User, Ingredient, Tag, RecipeIngredient, RecipeInstruction

# Register your models here.
admin.site.register(User)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeInstruction)
