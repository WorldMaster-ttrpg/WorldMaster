#!/bin/sh

set -euvf

if ! [ -e "$VENV/bin/activate" ]; then
  python3 -mvenv "$VENV"
  "$VENV/bin/pip" install -e .
fi

fixtures=${worldmaster_fixtures:-./fixtures}
mkdir -p "$fixtures"

exec "$VENV/bin/python" ./manage.py dumpdata \
  -o "$fixtures/$(date +%FT%H-%M-%S).json" \
  --natural-foreign \
  --natural-primary
