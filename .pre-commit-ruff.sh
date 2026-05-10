#!/usr/bin/env sh

set -e
uv run --group dev ruff check .
uv run --group dev ruff format --check .
