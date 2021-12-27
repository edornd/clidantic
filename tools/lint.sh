#!/usr/bin/env bash

set -e
set -x
# format with black and isort, then run flake8
poetry run black clidantic tests --check
poetry run isort clidantic tests --check-only
poetry run flake8 --max-line-length=120 clidantic tests