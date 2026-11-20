#!/usr/bin/env bash
# PostToolUse: formats and lint-fixes a mod file Claude just edited; lint errors Biome cannot fix go back to Claude.

set -euo pipefail

file_path=$(jq -r '.tool_input.file_path // empty')

case "$file_path" in
  "$CLAUDE_PROJECT_DIR"/mods/*.ts | "$CLAUDE_PROJECT_DIR"/mods/*.tsx | "$CLAUDE_PROJECT_DIR"/mods/*.json) ;;
  *) exit 0 ;;
esac

readonly biome="$CLAUDE_PROJECT_DIR/node_modules/.bin/biome"
# Before `npm install` there is no Biome; scripts/test.sh still catches the file then.
[[ -x "$biome" ]] || exit 0

if ! output=$("$biome" check --write --no-errors-on-unmatched "$file_path" 2>&1); then
  echo "$output" >&2
  exit 2
fi
