#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

uv run pytest "$@"

npm run lint

uv run scripts/build.py --check
