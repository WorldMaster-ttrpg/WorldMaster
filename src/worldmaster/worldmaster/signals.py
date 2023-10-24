from __future__ import annotations

from contextlib import closing
from typing import Any, cast

from django.db.backends.signals import connection_created
from django.db.backends.sqlite3.base import DatabaseWrapper, SQLiteCursorWrapper
from django.dispatch import receiver


@receiver(connection_created)
def configure_sqlite(sender, connection: Any, **kwargs):
    if isinstance(connection, DatabaseWrapper):
        with closing(cast(SQLiteCursorWrapper, connection.cursor())) as cursor:
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA case_sensitive_like = true")

