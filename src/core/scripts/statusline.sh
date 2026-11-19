#!/usr/bin/env bash
# managed-by: https://github.com/lachtan/nicecode
# version: 1.0.0

# Statusline launcher: picks an available interpreter and passes stdin (JSON) through.
# Prefers Python; PowerShell is the fallback for Windows/git-bash without Python.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "$SCRIPT_DIR/statusline.py"
elif command -v pwsh >/dev/null 2>&1; then
    exec pwsh -File "$SCRIPT_DIR/statusline.ps1"
else
    echo "statusline.sh: neither python3 nor pwsh found in PATH" >&2
    exit 1
fi
