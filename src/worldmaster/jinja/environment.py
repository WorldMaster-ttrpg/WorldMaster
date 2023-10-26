"""Environments and filters to help render SQL with Jinja.

This tries to lean into idiomatic Django.  Vars are not substituted in directly,
but are rolled into a set of variables in the order that they are encountered.
"""
from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from jinja2 import Environment, StrictUndefined, pass_eval_context
from markupsafe import Markup

from .app_loader import AppLoader

if TYPE_CHECKING:
    from typing import Any

    from jinja2.nodes import EvalContext


@pass_eval_context
def sql_var(eval_ctx: EvalContext, value: Any, vars: list[Any]) -> str | Markup:
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
def environment() -> Environment:
    from worldmaster.jinja.database_bytecode_cache import DatabaseBytecodeCache

    env = Environment(
        loader=AppLoader(),
        autoescape=False,
        optimized=True,
        undefined=StrictUndefined,
        bytecode_cache=DatabaseBytecodeCache(),
    )
    env.filters["sql_var"] = sql_var
    return env
