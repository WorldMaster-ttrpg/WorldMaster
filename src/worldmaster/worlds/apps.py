from django.apps import AppConfig


class WorldsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "worldmaster.worlds"

    def ready(self):
        from . import signals # noqa
