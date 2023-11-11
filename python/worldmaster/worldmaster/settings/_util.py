from __future__ import annotations

import re
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from collections.abc import Callable

_SECRET_PATH_REPLACEMENT = re.compile(r"[-_ ]")

_SECRETS_PATH = Path(environ.get("SECRETS_PATH", "/run/secrets"))

def map_opt[T, U](value: T | None, callable: Callable[[T], U]) -> U | None:
    if value is None:
        return None
    return callable(value)

def _get_secret(name: str) -> str | None:
    """Get the unmodified secret from the secret name, or None
    """
    env_var_name = _SECRET_PATH_REPLACEMENT.sub("_", name.upper())

    if env_var_name in environ:
        return environ[env_var_name]

    file_name_var_name = f"{env_var_name}_FILE"
    if file_name_var_name in environ:
        file_name = environ[file_name_var_name]
    else:
        file_name = _SECRET_PATH_REPLACEMENT.sub("-", name.lower())
    file_path = _SECRETS_PATH / file_name
    if file_path.exists():
        return file_path.read_text()

    return None

_sentinal = object()

@overload
def get_secret[T](name: str, *, trim: bool = True, default: T) -> str | T:
    ...

@overload
def get_secret[T](name: str, *, trim: bool = True) -> str:
    ...

def get_secret[T](name: str, *, trim: bool = True, default: T = _sentinal) -> str | T:
    """Get the secret either from an environment variable or filesystem path.

    The environment variable will have the secret name converted to all caps and
    all spaces and hyphens will be turned to underscores.

    The filesystem path will have the secret name converted to all lowercase and
    all spaces and underscores will be turned to hyphens.

    Will also attempt to find {env_var}_FILE to potentially override the
    filename.
    """
    secret = _get_secret(name)

    if secret is None:
        if default is _sentinal:
            raise ValueError("Secret was not found")
        else:
            return default

    if trim:
        return secret.rstrip("\r\n")
    else:
        return secret
