# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

from . import *

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

LANGUAGE_CODE = LANGUAGE_CODE
SECRET_KEY = 'django-insecure-r32v4zqj9#4o2=2fl$de7n%4^=356mzqz)02io#))t^rz0*qs*'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_ROOT / 'db.sqlite3',
    }
}

