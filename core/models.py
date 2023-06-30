from django.db import models

from accounts.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return '<Ingredient name="{}">'.format(self.name)


class Tag(models.Model):
    name = models.CharField(max_length=255)


class Recipe(models.Model):
    # Fields from schema.org/Recipe
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.URLField(blank=True, null=True)
    # cooking_method = models.CharField(max_length=255)
    prep_time = models.DurationField(blank=True, null=True)
    cook_time = models.DurationField(blank=True, null=True)
    total_time = models.DurationField(blank=True, null=True)
    # nutrition = models.JSONField
    author = models.CharField(max_length=255)
    keywords = models.JSONField(
        default=list, blank=True
    )  # from schema.org / just for search
    publisher = models.CharField(max_length=255)
    publisher_url = models.URLField(blank=True, null=True)
    origin_url = models.URLField(blank=True, null=True)

    # custom fields
    tags = models.ManyToManyField(Tag, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    @classmethod
    def get_all_filtered(cls, user):
        return cls.objects.filter(
            ~models.Q(tags__in=user.preferences.hidden_recipe_tags.all()),
            ~models.Q(
                ingredients__ingredient__in=user.preferences.hidden_recipe_ingredients.all()
            ),
        )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)


class RecipeInstruction(models.Model):
    class Meta:
        ordering = ["step_no"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "step_no"], name="unique_recipe_step_nos"
            )
        ]

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="instructions"
    )
    step_no = models.IntegerField()
    text = models.TextField()
    # ingredients = models.ManyToManyField(RecipeIngredient)
