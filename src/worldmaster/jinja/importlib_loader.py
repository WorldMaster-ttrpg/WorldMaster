from __future__ import annotations

from hashlib import sha512
from importlib.resources import files
from typing import TYPE_CHECKING

from jinja2 import BaseLoader

if TYPE_CHECKING:
    from collections.abc import Callable

    from jinja2 import Environment


class ImportlibLoader(BaseLoader):
    """A Jinja2 Loader that uses importlib.resources to load templates.

    Uses a hash to check for updating.
    """

    def __init__(self, package_name: str, *package_path: str):
        traversable = files(package_name)
        for part in package_path:
            traversable /= part
        self.__files = traversable

    def get_source(self, environment: Environment, template: str) -> tuple[str, None, Callable[[], bool]]:
        file = self.__files / template

        source_bytes = file.read_bytes()
        source = source_bytes.decode("utf-8")
        hash = sha512()
        hash.update(source_bytes)
        digest = hash.digest()
        def uptodate():
            source_bytes = file.read_bytes()
            hash = sha512()
            hash.update(source_bytes)
            return digest == hash.digest()
        return (source, None, uptodate)
