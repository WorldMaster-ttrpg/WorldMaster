from __future__ import annotations

from django.db import models


class BytecodeCacheStorage(models.Model):
    """A backend cache storage for the database-backed bytecode cache.
    """

    key = models.TextField(
        unique=True,
        blank=False,
        null=False,
    )

    code = models.BinaryField(
        blank=False,
        null=False,
    )
