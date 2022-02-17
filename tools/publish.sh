#!/usr/bin/env bash

set -e
set -x

poetry publish --build --username ${PYPI_USERNAME:-__token__} --password $PYPI_PASSWORD
