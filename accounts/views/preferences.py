from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from accounts.forms import AuthenticationForm, RecipeFilterForm
from accounts.helper import LoginRequiredMixin
from accounts.models import InviteCode, UserPreferences


class PreferencesIndexView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/preferences_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invite_codes"] = InviteCode.objects.filter(
            created_by=self.request.user
        )
        user_preferences, _ = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        context["recipe_filter_form"] = RecipeFilterForm(instance=user_preferences)
        return context


class PreferencesHideRecipesView(View):
    def post(self, request):
        instance = UserPreferences.objects.get(user=self.request.user)
        form = RecipeFilterForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("accounts:preferences_index")
        invite_codes = InviteCode.objects.filter(created_by=self.request.user)
        return render(
            request,
            "accounts/preferences_index.html",
            {"invite_codes": invite_codes, "recipe_filter_form": form},
        )


class CreateInviteCodeView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        invite_code = InviteCode(created_by=self.request.user)
        invite_code.save()
        return redirect("accounts:preferences_index")
