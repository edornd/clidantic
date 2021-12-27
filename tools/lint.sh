#!/usr/bin/env bash

set -e
set -x
# format with black and isort, then run flake8
black typer tests --check
isort typer tests --check-only
flake8 --max-line-length=120 clidantic