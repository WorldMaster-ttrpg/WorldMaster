from __future__ import annotations

from typing import TYPE_CHECKING

from .environment import environment

if TYPE_CHECKING:
    from jinja2 import Template


def get_template(name: str) -> Template:
    return environment().get_template(name)
