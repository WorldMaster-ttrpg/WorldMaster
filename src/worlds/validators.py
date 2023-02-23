from collections.abc import Iterator, Sequence, Mapping, Iterable
from django.core.exceptions import ValidationError
from typing import Iterable, TypeVar, cast
from operator import mul

T = TypeVar('T')

Vector = tuple[int, int]
Line = tuple[Vector, Vector]

def pairs(i: Iterable[T]) -> Iterator[tuple[T, T]]:
    '''Iterate over sliding pairs of iterable.
    '''

    yielding = False
    previous = False

    for item in i:
        if yielding:
            yield cast(T, previous), item
        else:
            yielding = True

        previous = item

def add(a: Vector, b: Vector) -> Vector:
    return (a[0] + b[0], a[1] + b[1])

def sub(a: Vector, b: Vector) -> Vector:
    return (a[0] - b[0], a[1] - b[1])

def cross(a: Vector, b: Vector) -> int:
    return a[0] * b[1] - a[1] * b[0]

def dot (a: Vector, b: Vector) -> int:
    return sum(ax * bx for ax, bx in zip(a, b))

def intersects(a: Line, b: Line) -> bool:
    p = a[0]
    r = sub(a[1], p)
    q = b[0]
    s = sub(b[1], q)

    cross_r_s = cross(r, s)
    sub_q_p = sub(q, p)
    if cross_r_s == 0:
        sub_q_p_cross_r = cross(sub_q_p, r)
        if sub_q_p_cross_r == 0:
            r_dot_r = dot(r, r)
            t0 = dot(sub_q_p, r) / r_dot_r
            t1 = dot(sub(add(q, s), p), r) / r_dot_r

            if t1 < t0:
                t0, t1 = t1, t0

            return 0.0 <= t0 <= 1.0 or 0.0 <= t1 <= 1.0 or (t0 < 0.0 and t1 > 1.0)
        else:
            return False
    else:
        t = cross(sub_q_p, s) / cross_r_s
        u = cross(sub_q_p, r) / cross_r_s
        return 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0

def validate_point(value) -> None:
    '''Validates that the value is a two-item sequence of integers.
    '''
    if not (
        isinstance(value, Sequence)
        and len(value) == 2
        and all(isinstance(c, int) for c in value)):
        raise ValidationError('point must be a three-item tuple of integers')

def validate_shape(value) -> None:
    '''Validates the value as a shape.

    * The value must have a non-empty "points" array without repeating points.

        * There must be at least 3 points

        * Each point is a part of an implicitly-closed 2D shape.

        * No pair of line segments may intersect.

    * The value must have a positive "height" integer.
    '''

    if not (
        isinstance(value, Mapping)
        and isinstance(value.get('height'), int)
        and value['height'] > 0
        and isinstance(value.get('points'), Sequence)
        and len(value['points']) >= 3
        and all(map(validate_point, value['points']))):

        raise ValidationError('shape must have points and a height')

    raw_points: Sequence[Sequence[int]] = value['points']
    points = [tuple(point) for point in raw_points]
    if len(points) != len({tuple(point) for point in points}):
        raise ValidationError('shape may not have duplicate points')

    segments = list(pairs(points)) + [(points[-1], points[0])]

    while len(segments) > 1:
        test = segments.pop()
        if any(intersects(test, other) for other in segments):
            raise ValidationError('no line segments in shape may intersect')
