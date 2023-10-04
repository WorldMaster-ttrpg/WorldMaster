from django.apps import AppConfig


class WikiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "worldmaster.wiki"

    def ready(self):
        from . import signals # noqa
