from django.contrib.auth.views import LoginView

from accounts.forms import AuthenticationForm


# Create your views here.
class LoginView(LoginView):
    authentication_form = AuthenticationForm
