from django.contrib import admin

from core.models import Recipe, User, Ingredient, Tag, RecipeIngredient, RecipeInstruction

# Register your models here.
admin.site.register(User)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)


class RecipeIngredientAdmin(admin.ModelAdmin):

    list_display = ['pk', 'unit', 'quantity', 'ingredient', 'description', 'recipe']


admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeInstruction)
