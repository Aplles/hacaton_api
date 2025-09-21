import os
from pathlib import Path

import environ

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", cast=str)
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", cast=str)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")])

CORS_ALLOWED_ORIGINS = env(
    "CORS_ALLOWED_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")]
)

BASE_DOMAIN = (
    f"{env('SCHEMA', default='http')}://{env('DOMAIN', default='localhost:8000')}"
)

CSRF_TRUSTED_ORIGINS = env(
    "CSRF_TRUSTED_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")]
)

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "solo",
    "rest_framework",
    "rest_framework.authtoken",
    "service_objects",
    "corsheaders",
    "drf_spectacular",
    "api",
    "models_app",
]

MIDDLEWARE = [
    "log_request_id.middleware.RequestIDMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "api.middleware.ForceLoginMiddleware",
]

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "conf.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

STATIC_URL = env("STATIC_URL", cast=str, default="/static/")
STATIC_ROOT = os.path.join(BASE_DIR, env("STATIC_ROOT", cast=str, default="static"))
MEDIA_ROOT = os.path.join(BASE_DIR, "uploads/")
MEDIA_URL = "/uploads/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

APPEND_SLASH = False

AUTH_USER_MODEL = "models_app.User"

if os.environ.get("PROFILE_ENABLED"):
    MIDDLEWARE += ["pyinstrument.middleware.ProfilerMiddleware"]
    PYINSTRUMENT_PROFILE_DIR = "profiles"

if os.environ.get("QUERY_COUNT_ENABLED"):
    MIDDLEWARE += ["querycount.middleware.QueryCountMiddleware"]
    QUERYCOUNT = {
        "THRESHOLDS": {
            "MEDIUM": 50,
            "HIGH": 200,
            "MIN_TIME_TO_LOG": 0,
            "MIN_QUERY_COUNT_TO_LOG": 0,
        },
        "IGNORE_REQUEST_PATTERNS": [],
        "IGNORE_SQL_PATTERNS": [],
        "DISPLAY_DUPLICATES": True,
        "RESPONSE_HEADER": "X-DjangoQueryCount-Count",
    }
