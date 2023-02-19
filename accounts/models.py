import datetime
import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.db import models


class User(AbstractBaseUser):
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "name"]

    username = models.CharField(unique=True, max_length=255)
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


def invite_code_default_expiry():
    return datetime.datetime.now() + datetime.timedelta(days=7)


class InviteCode(models.Model):
    code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expires = models.DateTimeField(default=invite_code_default_expiry)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    @classmethod
    def is_code_valid(cls, code):
        try:
            cls.objects.get(code=code, expires__gt=datetime.datetime.now())
            return True
        except cls.DoesNotExist:
            return False


class UserPreferences(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="preferences"
    )
    hidden_recipe_tags = models.ManyToManyField("core.Tag")
    hidden_recipe_ingredients = models.ManyToManyField("core.Ingredient")
