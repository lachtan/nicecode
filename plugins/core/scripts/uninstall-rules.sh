#!/bin/bash
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
TARGET_DIR="$PROJECT_DIR/.claude/rules/plugins/nicecode/core"

if [ -L "$TARGET_DIR" ]; then
    rm "$TARGET_DIR"
    echo "Removed symlink $TARGET_DIR."
elif [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
    echo "Removed directory $TARGET_DIR."
else
    echo "No nicecode rules found in this project."
fi
