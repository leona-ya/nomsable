from . import views
from django.urls import path, include

from .views import LoginView

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
]
