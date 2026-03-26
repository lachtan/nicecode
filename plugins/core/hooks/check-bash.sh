#!/usr/bin/env bash

file=$(jq -r '.tool_input.file_path // ""')

if [[ "$file" != *.sh ]]; then
  exit 0
fi

if ! command -v shellcheck &> /dev/null; then
  echo "Warning: shellcheck not found — bash lint was skipped. Install with: apt install shellcheck" >&2
  exit 0
fi

shellcheck "$file"
