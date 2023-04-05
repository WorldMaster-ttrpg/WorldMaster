#!/bin/sh

set -euvf

tsc --outDir "${worldmaster_static:-./static}"

exec watchexec -e ts -w ./ts -vv -- tsc --outDir "${worldmaster_static:-./static}"