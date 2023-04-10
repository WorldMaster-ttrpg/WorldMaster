#!/bin/sh

set -euvf

if ! [ -e /mnt/venv/bin/activate ]; then
  python3 -mvenv /mnt/venv
  /mnt/venv/bin/pip install -e .
fi

fixtures=${worldmaster_fixtures:-./fixtures}
mkdir -p "$fixtures"

exec /mnt/venv/bin/python ./manage.py dumpdata -o "$fixtures/$(date +%FT%H-%M-%S).json"
