from __future__ import annotations

from contextlib import suppress

from jinja2 import BytecodeCache
from jinja2.bccache import Bucket

from .models import BytecodeCacheStorage


class DatabaseBytecodeCache(BytecodeCache):
    def clear(self):
        BytecodeCacheStorage.objects.all().delete()

    def load_bytecode(self, bucket: Bucket) -> None:
        with suppress(BytecodeCacheStorage.DoesNotExist):
            bucket.bytecode_from_string(BytecodeCacheStorage.objects.get(key=bucket.key).code)

    def dump_bytecode(self, bucket: Bucket) -> None:
        BytecodeCacheStorage.objects.update_or_create(
            key=bucket.key,
            defaults={
                "code": bucket.bytecode_to_string(),
            },
        )
