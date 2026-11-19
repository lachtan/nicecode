#!/usr/bin/env python3
import json
import math
import os
import re
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

COMPUTER_ICON = "🖥️"
FOLDER_ICON = "📁"
BRANCH_ICON = "🌿"
MODEL_ICON = "💡"
TOKENS_IN_ICON = "↓"
TOKENS_OUT_ICON = "↑"
BAR_FILLED = "▓"
BAR_EMPTY = "░"

ANSI_RESET = "\x1b[0m"
ANSI_RED = "\x1b[31m"
ANSI_GREEN = "\x1b[32m"
ANSI_YELLOW = "\x1b[33m"
ANSI_ORANGE = "\x1b[38;5;208m"

MODEL_COLOR = ANSI_ORANGE
EFFORT_COLOR = ANSI_YELLOW


def format_token_count(value: int | None) -> str:
    if value is None:
        return "0"
    for divisor, suffix in ((1_000_000, "M"), (1_000, "k")):
        if value >= divisor:
            return f"{value / divisor:.1f}".removesuffix(".0") + suffix
    return str(round(value))


@dataclass(frozen=True)
class TokenCacheState:
    # Already-processed transcript offset, the running total, and the last counted
    # message.id (lines of one API response are contiguous, so this single id is enough
    # to dedup across a read boundary). Dedup is required because one response spans
    # several transcript lines with the same output_tokens.
    offset: int = 0
    total: int = 0
    last_id: str = ""


def read_token_cache_state(cache_file: Path) -> TokenCacheState:
    if not cache_file.is_file():
        return TokenCacheState()
    try:
        cache = json.loads(cache_file.read_text(encoding="utf-8"))
        return TokenCacheState(
            offset=int(cache.get("offset", 0)),
            total=int(cache.get("total", 0)),
            last_id=str(cache.get("lastId", "")),
        )
    except Exception:
        return TokenCacheState()


def save_token_cache_state(cache_file: Path, state: TokenCacheState) -> None:
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"offset": state.offset, "total": state.total, "lastId": state.last_id}
    cache_file.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def read_transcript_tail(transcript: Path, offset: int) -> bytes:
    with transcript.open("rb") as f:
        f.seek(offset)
        return f.read()


def add_output_tokens(state: TokenCacheState, new_bytes: bytes) -> TokenCacheState:
    # Process only complete lines; leave a partially written last line for next time.
    last_newline = new_bytes.rfind(b"\n")
    if last_newline < 0:
        return state

    complete_bytes = new_bytes[: last_newline + 1]
    total = state.total
    last_id = state.last_id

    for line in complete_bytes.decode("utf-8", errors="replace").split("\n"):
        if '"type":"assistant"' not in line:
            continue
        try:
            entry = json.loads(line)
            message = entry.get("message") or {}
            output_tokens = (message.get("usage") or {}).get("output_tokens")
            message_id = str(message.get("id") or "")
            if output_tokens and message_id and message_id != last_id:
                total += output_tokens
                last_id = message_id
        except Exception:
            pass

    return TokenCacheState(offset=state.offset + len(complete_bytes), total=total, last_id=last_id)


def get_cumulative_output_tokens(session_id: str | None, transcript_path: str | None) -> int:
    if not transcript_path:
        return 0
    transcript = Path(transcript_path)
    if not transcript.is_file():
        return 0

    cache_file = Path.home() / ".claude" / "session-env" / str(session_id) / "statusline-out.json"
    state = read_token_cache_state(cache_file)

    file_length = transcript.stat().st_size
    if file_length < state.offset:
        # New or truncated session — start from zero.
        state = TokenCacheState()
    if file_length <= state.offset:
        return state.total

    state = add_output_tokens(state, read_transcript_tail(transcript, state.offset))
    save_token_cache_state(cache_file, state)

    return state.total


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
    model_name = re.sub(r"\s*\(.*\)$", "", model.get("display_name") or "")

    ctx = data.get("context_window") or {}
    used_pct = round(ctx.get("used_percentage") or 0)
    total_input = ctx.get("total_input_tokens") or 0
    total_output = get_cumulative_output_tokens(data.get("session_id"), data.get("transcript_path"))

    bar_width = 10
    filled = min(bar_width, math.floor(used_pct * bar_width / 100))
    bar = (BAR_FILLED * filled) + (BAR_EMPTY * (bar_width - filled))

    if used_pct >= 90:
        bar_color = ANSI_RED
    elif used_pct >= 70:
        bar_color = ANSI_YELLOW
    else:
        bar_color = ANSI_GREEN

    in_fmt = format_token_count(total_input)
    out_fmt = format_token_count(total_output)
    effort = (data.get("effort") or {}).get("level")

    segments = [f"{COMPUTER_ICON} {host_name}", f"{FOLDER_ICON} {cwd}"]
    if branch:
        segments.append(f"{BRANCH_ICON} {branch}")
    model_segment = f"{MODEL_ICON} {MODEL_COLOR}{model_name}{ANSI_RESET}"
    if effort:
        model_segment += f" / {EFFORT_COLOR}{effort}{ANSI_RESET}"
    segments.append(model_segment)

    segments.append(f"{used_pct}% {bar_color}{bar}{ANSI_RESET}")
    segments.append(f"{TOKENS_IN_ICON} {in_fmt} {TOKENS_OUT_ICON} {out_fmt}")

    sys.stdout.write(" | ".join(segments) + "\n")


if __name__ == "__main__":
    main()
