#!/bin/sh

set -euvf

if ! [ -e /mnt/venv/bin/activate ]; then
  python3 -mvenv /mnt/venv
  /mnt/venv/bin/pip install -e .
fi

/mnt/venv/bin/python ./manage.py migrate

exec /mnt/venv/bin/python ./manage.py runserver 0.0.0.0:8000