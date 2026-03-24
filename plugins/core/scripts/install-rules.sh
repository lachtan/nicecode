#!/bin/bash

set -euo pipefail

if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
    RULES_DIR="$CLAUDE_PLUGIN_ROOT/rules"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    RULES_DIR="$(realpath "${SCRIPT_DIR}/../rules")"
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
TARGET_DIR="$PROJECT_DIR/.claude/rules/nicecode"

warn_gitignore() {
    if ! git -C "$PROJECT_DIR" rev-parse --is-inside-work-tree &>/dev/null; then
        return
    fi
    local gitignore="$PROJECT_DIR/.gitignore"
    if [ ! -f "$gitignore" ] || ! grep -q '.claude/rules/nicecode' "$gitignore" 2>/dev/null; then
        echo "Warning: .claude/rules/nicecode/ is not in .gitignore. Add it to prevent committing user-specific symlinks."
    fi
}

if [ ! -d "$RULES_DIR" ]; then
    echo "Error: Rules directory not found at $RULES_DIR" >&2
    exit 1
fi

if [ -L "$TARGET_DIR" ] && [ "$(readlink "$TARGET_DIR")" = "$RULES_DIR" ]; then
    [ "${1:-}" != "--quiet" ] && echo "Rules already linked to $RULES_DIR"
    warn_gitignore
    exit 0
fi

if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
fi

mkdir -p "$(dirname "$TARGET_DIR")"
ln -s "$RULES_DIR" "$TARGET_DIR"

echo "Linked $TARGET_DIR -> $RULES_DIR"
warn_gitignore
