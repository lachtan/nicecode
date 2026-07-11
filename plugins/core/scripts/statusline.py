#!/usr/bin/env python3
import json
import math
import os
import socket
import subprocess
import sys
from pathlib import Path

COMPUTER_ICON = "🖥️"
FOLDER_ICON = "📁"
BRANCH_ICON = "🌿"
EFFORT_ICON = "💡"
BAR_FILLED = "▓"
BAR_EMPTY = "░"


def format_token_count(value: int | None) -> str:
    if value is None:
        return "0"
    for divisor, suffix in ((1_000_000, "M"), (1_000, "k")):
        if value >= divisor:
            return f"{value / divisor:.1f}".removesuffix(".0") + suffix
    return str(round(value))


def get_cumulative_output_tokens(session_id: str | None, transcript_path: str | None) -> int:
    # Cumulative output-token count for the session, computed incrementally.
    # The cache holds the already-processed transcript offset, the running total,
    # and the last counted message.id (lines of one API response are contiguous,
    # so this single id is enough to dedup across a read boundary). Dedup is
    # required because one response spans several transcript lines with the same
    # output_tokens.
    if not transcript_path:
        return 0
    transcript = Path(transcript_path)
    if not transcript.is_file():
        return 0

    cache_dir = Path.home() / ".claude" / "session-env" / str(session_id)
    cache_file = cache_dir / "statusline-out.json"

    offset = 0
    total = 0
    last_id = ""
    if cache_file.is_file():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
            offset = int(cache.get("offset", 0))
            total = int(cache.get("total", 0))
            last_id = str(cache.get("lastId", ""))
        except Exception:
            pass

    file_length = transcript.stat().st_size
    if file_length < offset:
        # New or truncated session — start from zero.
        offset = 0
        total = 0
        last_id = ""

    if file_length > offset:
        with transcript.open("rb") as f:
            f.seek(offset)
            new_bytes = f.read()

        # Process only complete lines; leave a partially written last line for next time.
        last_newline = new_bytes.rfind(b"\n")
        if last_newline >= 0:
            complete_bytes = new_bytes[: last_newline + 1]
            offset += len(complete_bytes)

            for line in complete_bytes.decode("utf-8", errors="replace").split("\n"):
                if '"type":"assistant"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                    message = entry.get("message") or {}
                    ot = (message.get("usage") or {}).get("output_tokens")
                    entry_id = str(message.get("id") or "")
                    if ot and entry_id and entry_id != last_id:
                        total += ot
                        last_id = entry_id
                except Exception:
                    pass

        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps({"offset": offset, "total": total, "lastId": last_id}, separators=(",", ":")),
            encoding="utf-8",
        )

    return total


def main() -> None:
    data = json.load(sys.stdin)

    workspace = data.get("workspace") or {}
    cwd = workspace.get("current_dir") or data.get("cwd")

    host_name = (os.environ.get("COMPUTERNAME") or socket.gethostname()).lower()

    branch = ""
    if cwd:
        try:
            result = subprocess.run(
                ["git", "-C", cwd, "branch", "--show-current"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
        except Exception:
            branch = ""

    model = data.get("model") or {}
    model_name = (model.get("display_name") or "").partition(" (")[0].strip()

    ctx = data.get("context_window") or {}
    used_pct = round(ctx.get("used_percentage") or 0)
    context_size = ctx.get("context_window_size") or 0
    total_input = ctx.get("total_input_tokens") or 0
    total_output = get_cumulative_output_tokens(data.get("session_id"), data.get("transcript_path"))

    bar_width = 10
    filled = min(bar_width, math.floor(used_pct * bar_width / 100))
    bar = (BAR_FILLED * filled) + (BAR_EMPTY * (bar_width - filled))

    esc = "\x1b"
    reset = f"{esc}[0m"
    if used_pct >= 90:
        bar_color = f"{esc}[31m"
    elif used_pct >= 70:
        bar_color = f"{esc}[33m"
    else:
        bar_color = f"{esc}[32m"

    in_fmt = format_token_count(total_input)
    out_fmt = format_token_count(total_output)
    size_fmt = format_token_count(context_size)
    effort = (data.get("effort") or {}).get("level")

    segments = [f"{COMPUTER_ICON} {host_name}", f"{FOLDER_ICON} {cwd}"]
    if branch:
        segments.append(f"{BRANCH_ICON} {branch}")
    segments.append(f"{model_name} {size_fmt}")
    if effort:
        segments.append(f"{EFFORT_ICON} {effort}")
    segments.append(f"{used_pct}% {bar_color}{bar}{reset}")
    segments.append(f"↓ {in_fmt} ↑ {out_fmt}")

    sys.stdout.write(" | ".join(segments) + "\n")


if __name__ == "__main__":
    main()
