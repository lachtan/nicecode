#!/usr/bin/env python3
"""PostToolUse hook: lint or format the edited file with every check that applies to its suffix.

A missing tool is skipped silently; the tools are optional (see the core README).
Any failure of an installed tool goes to Claude as additionalContext; the hook itself always exits 0.
"""

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

FORMATTER_PS1 = Path(__file__).parent / "format-powershell.ps1"


@dataclass(frozen=True)
class Check:
    name: str
    suffixes: tuple[str, ...]
    command: tuple[str, ...]  # the edited file is appended as the last argument


# Checks for the same suffix run in this order: markdownlint fixes the file before mermaid lints it.
CHECKS = [
    Check("ruff", (".py",), ("ruff", "format")),
    Check("shellcheck", (".sh",), ("shellcheck",)),
    Check("markdownlint", (".md",), ("markdownlint-cli2", "--fix")),
    Check("mermaid", (".md",), ("md-mermaid-lint",)),
    Check("psscriptanalyzer", (".ps1", ".psm1", ".psd1"), ("pwsh", "-NoProfile", "-File", str(FORMATTER_PS1))),
]


def edited_file() -> str | None:
    """Reads the hook JSON from stdin; returns tool_input.file_path, or None when there is none."""
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"{Path(sys.argv[0]).name}: failed to parse stdin: {e}", file=sys.stderr)
        # A hook that cannot read its input must not block the call.
        return None
    return data.get("tool_input", {}).get("file_path") or None


def run_check(check: Check, path: str) -> str | None:
    """Runs the check on path; returns the message for Claude, or None if the tool is missing or passed."""
    resolved = shutil.which(check.command[0])
    if resolved is None:
        return None
    command = " ".join(check.command)
    try:
        result = subprocess.run([resolved, *check.command[1:], path], capture_output=True, text=True, errors="replace")
    except OSError as e:
        return f"[{check.name}] `{command}` could not be started: {e}"
    if result.returncode == 0:
        return None
    output = (result.stdout + result.stderr).strip() or "(no output)"
    return (
        f"[{check.name}] `{command}` exited with code {result.returncode} after the edit. The output below is "
        f"either problems in the edited file or a failure of the tool itself:\n{output}"
    )


def tell_claude(context: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}))


def main():
    path = edited_file()
    if path is None:
        return
    messages = [run_check(check, path) for check in CHECKS if path.lower().endswith(check.suffixes)]
    reported = [message for message in messages if message is not None]
    if reported:
        tell_claude("\n\n".join(reported))


if __name__ == "__main__":
    main()
