# core/urls.py

from . import views
from django.urls import path, include

app_name = 'core'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add', views.ParserInsertView.as_view(), name='add'),
    path('recipe/<int:recipe_id>', views.RecipeView.as_view(), name='detail'),
    path('recipe/<int:recipe_id>/edit', views.EditView.as_view(), name='edit'),
]