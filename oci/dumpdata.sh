#!/bin/sh

set -euvf

venv=${venv:-$(mktemp -d)}

if ! [ -e "${venv}/bin/activate" ]; then
  python3 -mvenv "$venv"
  "$venv/bin/pip" install -e .
fi

fixtures=${worldmaster_fixtures:-./fixtures}
mkdir -p "$fixtures"

exec "$venv/bin/python" ./manage.py dumpdata -o "$fixtures/$(date +%FT%H-%M-%S).json"
