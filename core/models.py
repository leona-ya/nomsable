from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.db import models


class User(AbstractBaseUser):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    username = models.CharField(
        unique=True,
        max_length=255
    )
    email = models.EmailField(
        unique=True,
        max_length=255,
    )

    name = models.CharField(
        max_length=255,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    is_superuser = models.BooleanField(
        default=False,
    )

    objects = UserManager()

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return True

    def __str__(self):
        return "<User username={}>".format(self.username)


class Ingredient(models.Model):
    name = models.CharField(max_length=255)


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
    keywords = models.JSONField(default=list, blank=True)  # from schema.org / just for search
    publisher = models.CharField(max_length=255)
    publisher_url = models.URLField(blank=True, null=True)
    origin_url = models.URLField(blank=True, null=True)

    # custom fields
    tags = models.ManyToManyField(Tag, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    unit = models.CharField(max_length=100)
    quantity = models.FloatField()
    description = models.CharField(max_length=255, null=True, blank=True)


class RecipeInstruction(models.Model):
    class Meta:
        ordering = ['step_no']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'step_no'], name='unique_recipe_step_nos'
            )
        ]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="instructions")
    step_no = models.IntegerField()
    text = models.TextField()
    # ingredients = models.ManyToManyField(RecipeIngredient)
