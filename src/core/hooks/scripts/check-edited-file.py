#!/usr/bin/env python3
"""PostToolUse hook: lint or format the edited file with every check that applies to its suffix.

A missing tool is skipped silently; the tools are optional (see the core README).
Any failure of an installed tool goes to Claude as additionalContext; the hook itself always exits 0.
"""

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

FORMATTER_PS1 = Path(__file__).parent / "format-powershell.ps1"
PATCH_FILE_HEADER = re.compile(r"^\*\*\* (?P<action>Add|Update|Delete) File: (?P<path>.+)$")
PATCH_MOVE_TO = re.compile(r"^\*\*\* Move to: (?P<path>.+)$")


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


def edited_files() -> list[str]:
    """Reads the hook JSON from stdin; returns the files the edit left behind.

    Claude Code names the file in tool_input.file_path. Codex sends the apply_patch text in
    tool_input.command instead; its paths may be relative to the payload's cwd.
    """
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"{Path(sys.argv[0]).name}: failed to parse stdin: {e}", file=sys.stderr)
        # A hook that cannot read its input must not block the call.
        return []
    tool_input = data.get("tool_input", {})
    if tool_input.get("file_path"):
        return [tool_input["file_path"]]
    patch = tool_input.get("command")
    if not isinstance(patch, str):
        return []
    cwd = data.get("cwd")
    return [str(Path(cwd, path)) if cwd else path for path in patched_files(patch)]


def patched_files(patch: str) -> list[str]:
    """Added and updated files of an apply_patch; a moved file under its new name, a deleted one not at all."""
    files = []
    for line in patch.splitlines():
        header = PATCH_FILE_HEADER.match(line)
        move = PATCH_MOVE_TO.match(line)
        if header and header["action"] != "Delete":
            files.append(header["path"].strip())
        elif move:
            # apply_patch allows `Move to` only directly under an `Update File` header.
            files[-1] = move["path"].strip()
    return files


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
    messages = [
        run_check(check, path) for path in edited_files() for check in CHECKS if path.lower().endswith(check.suffixes)
    ]
    reported = [message for message in messages if message is not None]
    if reported:
        tell_claude("\n\n".join(reported))


if __name__ == "__main__":
    main()
