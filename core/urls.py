# core/urls.py

from . import views
from django.urls import path, include

app_name = 'core'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
