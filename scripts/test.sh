#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

uv run pytest "$@"

uv run scripts/build.py --check
