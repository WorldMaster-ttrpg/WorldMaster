"""Production settings."""


from . import *  # noqa: F403
from ._util import get_secret

DEBUG = False

SECRET_KEY = get_secret("secret key")
ALLOWED_HOSTS = (
    "staging.worldmaster.games",
    "worldmaster.games",
    "worldmaster.test",
)
CSRF_TRUSTED_ORIGINS = (
    "https://staging.worldmaster.games",
    "https://worldmaster.games",
    "https://worldmaster.test",
    "http://worldmaster.test",
)

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# TODO: Probably need to set staticfiles and stuff from environment variables
# so they can be collected in a production environment.  We should never need to
# set development settings for anything in production.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_secret("database name", default="worldmaster"),
        "USER": get_secret("database user", default="worldmaster"),
        "PASSWORD": get_secret("database password"),
        "HOST": get_secret("database host", default="postgres"),
        "PORT": int(get_secret("database port", default=5432)),
    },
}

