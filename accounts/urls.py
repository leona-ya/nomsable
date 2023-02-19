from django.urls import path

from accounts.views import auth, preferences

app_name = "accounts"
urlpatterns = [
    path("login/", auth.LoginView.as_view(), name="login"),
    path("signup/", auth.SignUpView.as_view(), name="signup"),
    path(
        "preferences/",
        preferences.PreferencesIndexView.as_view(),
        name="preferences_index",
    ),
    path(
        "preferences/create_invite_code",
        preferences.CreateInviteCodeView.as_view(),
        name="preferences_create_invite_code",
    ),
    path(
        "preferences/hide_recipes",
        preferences.PreferencesHideRecipesView.as_view(),
        name="preferences_hide_recipes",
    ),
]
