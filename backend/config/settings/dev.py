"""Настройки разработки. Используются по умолчанию (см. manage.py)."""

import os

from .base import *  # noqa: F401,F403
from .base import env_bool, env_list

DEBUG = env_bool("DJANGO_DEBUG", default=True)

# Дефолт — только для локальной разработки; prod требует ключ из окружения.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-do-not-use-in-prod",
)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1")

# Dev-origin SPA (Vite); переопределяется переменной CORS_ALLOWED_ORIGINS.
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
)
