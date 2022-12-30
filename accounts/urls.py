from django.urls import path

from accounts.views import auth, preferences

app_name = "accounts"
urlpatterns = [
    path("login/", auth.LoginView.as_view(), name="login"),
    # path(
    #     "preferences/",
    #     preferences.PreferencesIndexView.as_view(),
    #     name="preferences_index",
    # ),
]
