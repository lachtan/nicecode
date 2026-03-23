#!/usr/bin/env bash

file=$(jq -r '.tool_input.file_path // ""')

if [[ "$file" == *.py ]]; then
    ruff format "$file"
fi
