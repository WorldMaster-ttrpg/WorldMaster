#!/bin/sh

set -euvf

venv=${venv:-$(mktemp -d)}

if ! [ -e "${venv}/bin/activate" ]; then
  python3 -mvenv "$venv"
  "$venv/bin/pip" install -e .
fi

"$venv/bin/python" ./manage.py migrate

exec "$venv/bin/python" ./manage.py "$@"
