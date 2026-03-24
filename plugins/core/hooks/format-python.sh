#!/usr/bin/env bash

file=$(jq -r '.tool_input.file_path // ""')

if [[ "$file" == *.py ]]; then
    if ! command -v ruff &> /dev/null; then
        echo "Warning: ruff not found — Python format check was skipped. Install with: uv tool install ruff" >&2
        exit 1
    fi
    ruff format "$file"
fi
