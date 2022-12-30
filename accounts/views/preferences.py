from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from accounts.forms import AuthenticationForm
from accounts.helper import LoginRequiredMixin
from accounts.models import InviteCode


class PreferencesIndexView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/preferences_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invite_codes"] = InviteCode.objects.filter(created_by=self.request.user)
        return context

class CreateInviteCodeView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        invite_code = InviteCode(created_by=self.request.user)
        invite_code.save()
        return redirect("accounts:preferences_index")
