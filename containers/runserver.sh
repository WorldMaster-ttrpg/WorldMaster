#!/bin/sh

exec "$VENV/bin/python" -X dev -X tracemalloc=25 -mdjango runserver 0.0.0.0:8000
