#!/bin/sh

set -euvf

venv=${venv:-$(mktemp -d)}

if ! [ -e "${venv}/bin/activate" ]; then
  python3 -mvenv "$venv"
fi
"$venv/bin/pip" install -e .

"$venv/bin/python" ./manage.py migrate

exec "$venv/bin/python" ./manage.py "$@"
