#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_DIR="${SCRIPT_DIR}/../rules"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
TARGET_DIR="$PROJECT_DIR/.claude/rules/nicecode"

if [ ! -d "$RULES_DIR" ]; then
    echo "Error: Rules directory not found at $RULES_DIR" >&2
    exit 1
fi

mkdir -p "$TARGET_DIR"

installed=0

for rule in "$RULES_DIR"/*.md; do
    filename="$(basename "$rule")"
    cp "$rule" "$TARGET_DIR/$filename"
    echo "  Installed: $filename"
    installed=$((installed + 1))
done

echo ""
echo "Done. Installed $installed rules to $TARGET_DIR."
