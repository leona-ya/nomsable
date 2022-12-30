# core/urls.py

from django.urls import include, path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("add", views.ParserInsertView.as_view(), name="add"),
    path("about", views.AboutView.as_view(), name="about"),
    path("search", views.SearchView.as_view(), name="search"),
    path("recipe/<int:recipe_id>", views.RecipeView.as_view(), name="detail"),
    path("recipe/<int:recipe_id>/edit", views.EditView.as_view(), name="edit"),
]
