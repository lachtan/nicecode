#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_DIR="$(realpath "${SCRIPT_DIR}/../rules")"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
TARGET_DIR="$PROJECT_DIR/.claude/rules/nicecode"

if [ ! -d "$RULES_DIR" ]; then
    echo "Error: Rules directory not found at $RULES_DIR" >&2
    exit 1
fi

# Remove old install (copy-based directory or stale symlink)
if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
fi

mkdir -p "$(dirname "$TARGET_DIR")"
ln -s "$RULES_DIR" "$TARGET_DIR"

echo "Linked $TARGET_DIR -> $RULES_DIR"
