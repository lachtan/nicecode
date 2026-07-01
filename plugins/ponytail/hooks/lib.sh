#!/usr/bin/env bash
# Shared helpers for ponytail hooks. Sourced, not executed.

# Extract a validated session_id from a hook JSON payload.
# Prints the id, or nothing if it is missing or not a safe path component.
ponytail_session_id() {
  local payload="$1"
  local sid

  if ! command -v jq &> /dev/null; then
    echo "ponytail: jq not found — hook disabled. Install with: apt install jq" >&2
    exit 1
  fi

  sid="$(echo "$payload" | jq -r '.session_id // ""')"

  if [[ ! "$sid" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo "ponytail: session id not found" >&2
    exit 1
  fi

  echo "$sid"
}

# Per-session marker path for a given session id.
ponytail_marker() {
  local sid="$1"

  echo "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/session-env/$sid/ponytail-active"
}

# Print marker path for the session in the payload; return 1 if no valid sid.
ponytail_marker_from_payload() {
  local payload="$1"
  local sid

  sid="$(ponytail_session_id "$payload")"
  if [[ -z "$sid" ]]; then
    echo "ponytail: no valid session id in payload" >&2
    exit 1
  fi

  ponytail_marker "$sid"
}

# Print SKILL.md body without its YAML frontmatter.
ponytail_skill_body() {
  local skill="$1"

  awk 'c >= 2 { print; next } /^---[[:space:]]*$/ { c++ }' "$skill"
}
