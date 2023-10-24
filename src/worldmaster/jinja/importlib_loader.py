from __future__ import annotations

from importlib.resources import files
from typing import TYPE_CHECKING

from jinja2 import BaseLoader

if TYPE_CHECKING:
    from collections.abc import Callable

    from jinja2 import Environment


class ImportlibLoader(BaseLoader):
    """A Jinja2 Loader that uses importlib.resources to load templates.
    """

    def __init__(self, package_name: str, *package_path: str):
        traversable = files(package_name)
        for part in package_path:
            traversable /= part
        self.__files = traversable

    def get_source(self, environment: Environment, template: str) -> tuple[str, None, Callable[[], bool]]:
        file = self.__files / template
        return (file.read_text("utf-8"), None, lambda: True)
