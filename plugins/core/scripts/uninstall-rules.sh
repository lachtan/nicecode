#!/bin/bash
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
TARGET_DIR="$PROJECT_DIR/.claude/rules/nicecode"

if [ ! -d "$TARGET_DIR" ]; then
    echo "No nicecode rules found in this project."
    exit 0
fi

echo "The following rules will be removed:"
for file in "$TARGET_DIR"/*.md; do
    [ -f "$file" ] && echo "  $(basename "$file")"
done

rm -rf "$TARGET_DIR"
echo "Done. Removed $TARGET_DIR."
