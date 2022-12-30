from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import AuthenticationForm, UserCreationForm


# Create your views here.
class LoginView(LoginView):
    authentication_form = AuthenticationForm


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "registration/signup.html"
