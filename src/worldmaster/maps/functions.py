from __future__ import annotations

from typing import Any, cast

from django.contrib.gis.db import models


class IsClosed(models.Func):
    function = "ST_IsClosed"
    arity = 1
    output_field = cast(Any, models.BooleanField())

class IsSimple(models.Func):
    function = "ST_IsSimple"
    arity = 1
    output_field = cast(Any, models.BooleanField())

class IsPolygonCW(models.Func):
    function = "ST_IsPolygonCW"
    arity = 1
    output_field = cast(Any, models.BooleanField())

class IsPolygonCCW(models.Func):
    function = "ST_IsPolygonCCW"
    arity = 1
    output_field = cast(Any, models.BooleanField())

class ForcePolygonCW(models.Func):
    function = "ST_ForcePolygonCW"
    arity = 1
    output_field = cast(Any, models.PolygonField())

class ForcePolygonCCW(models.Func):
    function = "ST_ForcePolygonCCW"
    arity = 1
    output_field = cast(Any, models.PolygonField())

class NRings(models.Func):
    function = "ST_NRings"
    arity = 1
    output_field = cast(Any, models.PositiveIntegerField())
