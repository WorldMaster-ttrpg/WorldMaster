from __future__ import annotations


class Vector2D:
    def __init__(self, x: int, y: int) -> None: ...
    x: int
    y: int

    @staticmethod
    def from_bytes(b: bytes, /) -> Vector2D: ...

    @staticmethod
    def from_json(j: bytes, /) -> Vector2D: ...

    def to_bytes(self) -> bytes: ...
    def to_json(self) -> str: ...

class Vector3D:
    def __init__(self, x: int, y: int, z: int) -> None: ...
    x: int
    y: int
    z: int

