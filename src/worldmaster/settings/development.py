# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

from . import * # noqa: F403
from pathlib import Path
from os import environ

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

SECRET_KEY = 'django-insecure-r32v4zqj9#4o2=2fl$de7n%4^=356mzqz)02io#))t^rz0*qs*'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_ROOT / 'dev' / 'db.sqlite3',
    }
}

STATICFILES_DIRS = [
    environ.get('worldmaster_static', PROJECT_ROOT / 'static'),
]

FIXTURE_DIRS = [
    environ.get('worldmaster_fixture', PROJECT_ROOT / 'fixtures'),
]
