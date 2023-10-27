from __future__ import annotations

from hashlib import sha512
from importlib.resources import files
from typing import TYPE_CHECKING

from django.apps import apps
from jinja2 import BaseLoader, TemplateNotFound

if TYPE_CHECKING:
    from collections.abc import Callable

    from jinja2 import Environment


class AppLoader(BaseLoader):
    """A Jinja2 Loader that uses importlib.resources to load templates from Django apps.
    """

    def get_source(self, environment: Environment, template: str) -> tuple[str, None, Callable[[], bool]]:
        for app in apps.get_app_configs():
            file = files(app.name) / "templates" / template
            if file.is_file():
                source_bytes = file.read_bytes()
                source = source_bytes.decode("utf-8")
                hash = sha512()
                hash.update(source_bytes)
                digest = hash.digest()
                if __debug__:
                    def uptodate() -> bool:
                        source_bytes = file.read_bytes()
                        hash = sha512()
                        hash.update(source_bytes)
                        return digest == hash.digest()
                else:
                    def uptodate() -> bool:
                        return True
                return (source, None, uptodate)
        raise TemplateNotFound(template)
