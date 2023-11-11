# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

from os import environ
from pathlib import Path

from . import *  # noqa: F403

_project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

SECRET_KEY = "django-insecure-r32v4zqj9#4o2=2fl$de7n%4^=356mzqz)02io#))t^rz0*qs*"

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _project_root / "dev" / "db.sqlite3",
    },
}

STATICFILES_DIRS = [
    _project_root / "static",
]

FIXTURE_DIRS = [
    environ.get("WORLDMASTER_FIXTURE", _project_root / "fixtures"),
]
