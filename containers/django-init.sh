#!/bin/sh

set -euxf

if ! [ -e "$VENV/bin/activate" ]; then
  python3 -mvenv "$VENV"
fi
"$VENV/bin/pip" install -e .

"$VENV/bin/django-admin" migrate
