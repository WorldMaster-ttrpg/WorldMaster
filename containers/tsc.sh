#!/bin/sh

set -euxf

exec watchexec -e ts -w ./src -vv -- tsc