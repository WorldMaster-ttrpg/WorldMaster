"""Environments and filters to help render SQL with Jinja.

This tries to lean into idiomatic Django.  Vars are not substituted in directly
"""
from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from jinja2 import Environment, pass_eval_context
from markupsafe import Markup

from .importlib_loader import ImportlibLoader

if TYPE_CHECKING:
    from typing import Any

    from jinja2.nodes import EvalContext


@pass_eval_context
def var(eval_ctx: EvalContext, value: Any, vars: list[Any]) -> str | Markup:
    """Substitute the variable to a placeholder and push it to a parameter
    array.

    Pass the variable and the parameter list as arguments.
    """
    vars.append(value)
    if eval_ctx.autoescape:
        return Markup("%s")
    else:
        return "%s"

@cache
def environment(package_name: str, *package_path: str) -> Environment:
    env = Environment(
        loader=ImportlibLoader(package_name, *package_path),
        autoescape=False,
        optimized=True,
    )
    env.filters["var"] = var
    return env

