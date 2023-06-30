from django.contrib import admin

from core.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeInstruction,
    Tag,
    User,
)

# Register your models here.
admin.site.register(User)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)


class RecipeIngredientAdmin(admin.ModelAdmin):

    list_display = ["pk", "quantity", "ingredient", "description", "recipe"]


admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeInstruction)
