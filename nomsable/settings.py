"""
Django settings for nomsable project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import configparser
import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key

config = configparser.RawConfigParser()
config.read_file(
    open(os.environ.get("NOMSABLE_CONFIG_FILE", "nomsable.cfg"), encoding="utf-8")
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


if config.has_option("general", "secret_key"):
    secret_key = config.get("general", "secret_key")
else:
    secret_key = os.environ.get("NOMSABLE_SECRET_KEY", get_random_secret_key())

SECRET_KEY = secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.getboolean("general", "debug", fallback=False)

ALLOWED_HOSTS = config.get("general", "allowed_hosts", fallback="*").split(",")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "compressor",
    "accounts",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "nomsable.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["nomsable/templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "nomsable.wsgi.application"

db_backend = config.get("database", "engine", fallback="sqlite3")
if db_backend == "postgresql_psycopg2":
    db_backend = "postgresql"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends." + db_backend,
        "NAME": config.get("database", "name", fallback="db.sqlite3"),
        "USER": config.get("database", "user", fallback=""),
        "PASSWORD": config.get("database", "password", fallback=""),
        "HOST": config.get("database", "host", fallback=""),
        "PORT": config.get("database", "port", fallback=""),
        "CONN_MAX_AGE": 0 if db_backend == "sqlite3" else 120,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = config.get("general", "time_zone", fallback="UTC")

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

STATIC_ROOT = config.get(
    "general", "static_root", fallback=os.path.join(BASE_DIR, "static")
)

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_PRECOMPILERS = (("text/x-sass", "django_libsass.SassCompiler"),)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

LOGIN_REDIRECT_URL = "/"
