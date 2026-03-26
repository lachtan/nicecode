#!/usr/bin/env python3

import re
import json
import sys


FORBIDDEN = [
    "pip",
    "pip3",
    "pipx",
    "python -m pip",
    "python -m venv",
    "python -m ensurepip",
    "python3 -m pip",
    "python3 -m venv",
    "python3 -m ensurepip",
    "easy_install",
]


def verify(command: str) -> bool:
    for forbidden in FORBIDDEN:
        pattern = r"\b" + re.sub(r"\s+", r"\\s+", forbidden) + r"\b"
        if re.search(pattern, command):
            return False
    return True


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"check-uv: failed to parse stdin: {e}", file=sys.stderr)
        sys.exit(1)
    command = data.get("tool_input", {}).get("command", "").strip()
    command = " ".join(command.split())
    if re.match(r"^uvx?\s", command) and not re.search(r"[;&|]", command):
        return
    if not verify(command):
        print(f"Forbidden: '{command}' detected. Use 'uv' instead.", file=sys.stderr)
        print("See .claude/skills/python-env/SKILL.md for alternatives.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
