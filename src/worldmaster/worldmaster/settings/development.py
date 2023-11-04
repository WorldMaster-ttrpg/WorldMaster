# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

from os import environ
from pathlib import Path

from . import *  # noqa: F403

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

SECRET_KEY = "django-insecure-r32v4zqj9#4o2=2fl$de7n%4^=356mzqz)02io#))t^rz0*qs*"

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": PROJECT_ROOT / "dev" / "db.sqlite3",
    },
}

# STATIC_ROOT = environ.get("WORLDMASTER_STATIC", PROJECT_ROOT / "static")

STATICFILES_DIRS = [
    PROJECT_ROOT / "static",
]

FIXTURE_DIRS = [
    environ.get("WORLDMASTER_FIXTURE", PROJECT_ROOT / "fixtures"),
]
