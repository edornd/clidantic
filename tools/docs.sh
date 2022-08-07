#!/usr/bin/env bash

set -e
set -x
# run mkdocs to publish to gh-pages
poetry run mkdocs gh-deploy --force
