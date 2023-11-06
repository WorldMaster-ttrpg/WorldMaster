from __future__ import annotations

from typing import Any, cast

from django.db import models


class IsClosed(models.Func):
    function = "ST_IsClosed"
    arity = 1
    output_field = cast(Any, models.BooleanField())
