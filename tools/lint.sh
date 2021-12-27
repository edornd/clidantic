#!/usr/bin/env bash

set -e
set -x
# format with black and isort, then run flake8
poetry run black clidantic tests --check
isort clidantic tests --check-only
flake8 --max-line-length=120 clidantic tests