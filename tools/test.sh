#!/usr/bin/env bash

set -e
set -x

# Use xdist-pytest --forked to ensure modified sys.path to import relative modules in examples keeps working
poetry run pytest --cov=clidantic --cov=examples --cov-report=xml -o console_output_style=progress
