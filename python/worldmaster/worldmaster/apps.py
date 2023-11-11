from django.apps import AppConfig


class WorldmasterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "worldmaster.worldmaster"

    def ready(self):
        from . import signals # noqa
