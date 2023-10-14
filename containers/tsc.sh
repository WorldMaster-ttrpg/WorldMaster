#!/bin/sh

set -euxf

${YARN:-yarn} build

exec watchexec -e mts -w ./ts -vv -- ${YARN:-yarn} build