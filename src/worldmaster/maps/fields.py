from __future__ import annotations

import struct
import sys
from io import BytesIO
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from typing import Any

type Point = tuple[float, float, float]

# A single-ring polygon
type Polygon = tuple[Point, ...]
type Polyhedron = tuple[Polygon, ...]

_little_endian = sys.byteorder == "little"

_point_header = struct.pack(
    "=BLL",
    _little_endian,
    # Z and SRID flags + geometry type
    0x80000000 | 0x20000000 | 1,
    # 0 SRID
    0,
)

_polygon_header = struct.pack(
    "=BLL",
    _little_endian,
    # Z and SRID flags + geometry type
    0x80000000 | 0x20000000 | 3,
    # 0 SRID
    0,
)

_polyhedron_header = struct.pack(
    "=BLL",
    _little_endian,
    # Z and SRID flags + geometry type
    0x80000000 | 0x20000000 | 15,
    # 0 SRID
    0,
)

def _point_to_ewkb(point: Point) -> bytes:
    return struct.pack("=3d", *point)

def _point_to_full_ewkb(point: Point) -> bytes:
    return _point_header + _point_to_ewkb(point)

def _polygon_to_ewkb(polygon: Polygon) -> bytes:
    count = len(polygon)
    # Just consider the polygon to have 0 rings if it doesn't have any points.
    # This probably shouldn't ever happen.
    if count == 0:
        return b"\x00\x00\x00\x00"

    with BytesIO() as io:
        # Always 1 ring for our use.
        io.write(struct.pack("=L", 1))
        io.write(struct.pack("=L", count))
        for point in polygon:
            io.write(_point_to_ewkb(point))
        return io.getvalue()

def _polygon_to_full_ewkb(polygon: Polygon) -> bytes:
    return _polygon_header + _polygon_to_ewkb(polygon)

def _polyhedron_to_ewkb(polyhedron: Polyhedron) -> bytes:
    count = len(polyhedron)
    # This probably shouldn't ever happen.
    if count == 0:
        return b"\x00\x00\x00\x00"

    with BytesIO() as io:
        io.write(struct.pack("=L", count))
        for polygon in polyhedron:
            io.write(_polygon_to_full_ewkb(polygon))
        return io.getvalue()

def _polyhedron_to_full_ewkb(polyhedron: Polyhedron) -> bytes:
    return _polyhedron_header + _polyhedron_to_ewkb(polyhedron)

class PointField(models.Field):
    description = "A PostGIS geometry(PointZ, 0) field"
    GEOMETRY_TYPE = 1001

    def db_type(self, connection):
        return "geometry(PointZ, 0)"

    def get_prep_value(self, value: Point | None) -> Any:
        if value is None:
            return None

        return _point_to_full_ewkb(value)

class PolyhedralSurfaceField(models.Field):
    description = "A PostGIS geometry(PolyhedralSurfaceZ, 0) field"
    GEOMETRY_TYPE = 15

    def db_type(self, connection):
        return "geometry(PolyhedralSurfaceZ, 0)"

    def get_prep_value(self, value: Polyhedron | None) -> Any:
        if value is None:
            return None

        return _polyhedron_to_full_ewkb(value)

    def from_db_value(self, value, expression, connection) -> Polyhedron:
        raise NotImplementedError

