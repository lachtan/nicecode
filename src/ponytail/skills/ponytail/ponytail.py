"""Ponytail hook — one script for both events, driven by the payload.

UserPromptSubmit: `/ponytail on|anchor` writes a per-session marker,
`/ponytail off` / `stop ponytail` removes it; while the marker exists the short
anchor is injected every turn. SessionStart: reload the full ruleset while the
marker exists. Plain `/ponytail` (or a model-invoked skill) is one-shot and
touches no marker — that is the skill's own job, not this hook's.
"""

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

ACTIVATE = r"/ponytail\s+(?:on|anchor)\b"
DEACTIVATE = r"/ponytail\s+off\b|stop\s+ponytail\b"
SESSION_ID = r"[A-Za-z0-9_-]+"


def marker_path(payload: dict) -> Path | None:
    """Per-session marker path, or None if the session id is missing/unsafe."""
    sid = payload.get("session_id", "")
    if not re.fullmatch(SESSION_ID, sid):
        return None
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return Path(base) / "session-env" / sid / "ponytail-active"


def skill_body() -> str:
    """SKILL.md without its YAML frontmatter (lines after the second `---`)."""
    count = 0
    body = []
    for line in (HERE / "SKILL.md").read_text().splitlines(keepends=True):
        if count >= 2:
            body.append(line)
        elif line.strip() == "---":
            count += 1
    return "".join(body)


def handle_prompt(payload: dict) -> str:
    marker = marker_path(payload)
    if marker is None:
        return ""
    prompt = payload.get("prompt", "")
    if re.search(DEACTIVATE, prompt, re.IGNORECASE):
        marker.unlink(missing_ok=True)
        return ""
    if re.search(ACTIVATE, prompt, re.IGNORECASE):
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
    if marker.exists():
        return (HERE / "anchor.txt").read_text()
    return ""


def handle_session_start(payload: dict) -> str:
    marker = marker_path(payload)
    if marker and marker.exists():
        return skill_body()
    return ""


def main() -> None:
    payload = json.load(sys.stdin)
    handler = {
        "UserPromptSubmit": handle_prompt,
        "SessionStart": handle_session_start,
    }.get(payload.get("hook_event_name"))
    if handler:
        sys.stdout.write(handler(payload))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # ponytail: swallow everything — a hook must never break the session.
        pass
