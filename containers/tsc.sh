#!/bin/sh

set -euxf

tsc --outDir "$WORLDMASTER_STATIC"

exec watchexec -e ts -w ./ts -vv -- tsc --outDir "$WORLDMASTER_STATIC"