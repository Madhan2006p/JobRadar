"""Django settings for JobRadar.

Every secret or machine-specific value comes from an environment variable,
with a safe local default. Never put real passwords or tokens in this file.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


# ---------------- Core ----------------
# The default key is for local development only. Set DJANGO_SECRET_KEY in production.
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-me")
DEBUG = env("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",  # ArrayField, GinIndex
    # Third-party
    "rest_framework",
    "corsheaders",
    # Our apps
    "jobs",
    "alerts",
    "reports",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be near the top
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jobradar.urls"
WSGI_APPLICATION = "jobradar.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------- Database (PostgreSQL in Docker) ----------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "jobradar"),
        "USER": env("POSTGRES_USER", "jobradar"),
        "PASSWORD": env("POSTGRES_PASSWORD", "jobradar"),
        "HOST": env("POSTGRES_HOST", "localhost"),
        "PORT": env("POSTGRES_PORT", "5432"),
        # Week 4: keep connections open between requests (a simple form of pooling)
        # "CONN_MAX_AGE": 60,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"

# ---------------- CORS (the frontend runs on port 5500) ----------------
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", "http://localhost:5500").split(",")

# ---------------- Django REST Framework ----------------
REST_FRAMEWORK = {
    # ?limit=20&offset=0 paging -> {"count", "next", "previous", "results"}
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    # ?search=python (SearchFilter) and ?ordering=-created_at (OrderingFilter)
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Learning project: open API, no login. Week 4 idea: add token auth.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    # TODO Week 3: rate limiting (DRF stores the counters in the cache = Redis)
    # "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    # "DEFAULT_THROTTLE_RATES": {"anon": "60/min"},
}

# ---------------- Redis, Celery, cache (Week 2 and 3) ----------------
REDIS_URL = env("REDIS_URL", "redis://localhost:6379/0")

# TODO Week 2: Celery reads every setting that starts with CELERY_
# CELERY_BROKER_URL = REDIS_URL
# CELERY_RESULT_BACKEND = REDIS_URL
# CELERY_TIMEZONE = TIME_ZONE
# CELERY_BEAT_SCHEDULE = {
#     "fetch-all-sources": {
#         "task": "jobs.tasks.fetch_all_sources",
#         "schedule": int(env("FETCH_EVERY_MINUTES", "60")) * 60,
#     },
# }

# TODO Week 3: use Redis as Django's cache (built into Django, no extra package)
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": REDIS_URL,
#     }
# }
JOBS_CACHE_SECONDS = int(env("JOBS_CACHE_SECONDS", "60"))

# ---------------- Alerts (Week 3) ----------------
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")  # empty = messages are only logged
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
