"""Shared helpers for the PostToolUse hooks that lint or format the edited file.

A missing tool is skipped silently; the tools are optional (see the core README).
Findings go to Claude as additionalContext; the hook itself always exits 0.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path


def edited_file(suffixes: tuple[str, ...]) -> str | None:
    """Reads the hook JSON from stdin; returns tool_input.file_path if it ends with one of suffixes."""
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"{Path(sys.argv[0]).name}: failed to parse stdin: {e}", file=sys.stderr)
        # A hook that cannot read its input must not block the call.
        return None
    path = data.get("tool_input", {}).get("file_path", "")
    if not path or not path.lower().endswith(suffixes):
        return None
    return path


def run_check(argv: list[str]) -> None:
    """Runs argv (the edited file last); missing tool -> silent return; non-zero exit -> prints additionalContext JSON."""
    resolved = shutil.which(argv[0])
    if resolved is None:
        return
    try:
        # The resolved path lets Windows run shims such as npx.cmd.
        result = subprocess.run([resolved, *argv[1:]], capture_output=True, text=True, errors="replace")
    except OSError as e:
        print(f"{argv[0]}: {e}", file=sys.stderr)
        return
    if result.returncode == 0:
        return
    output = (result.stdout + result.stderr).strip() or f"exited with code {result.returncode} and no output"
    command = " ".join(argv[:-1])
    context = f"{command} reported issues in the edited file:\n{output}"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}))
