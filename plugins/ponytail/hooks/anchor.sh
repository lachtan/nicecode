#!/usr/bin/env bash

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$here/lib.sh"

skill="$here/../skills/ponytail/SKILL.md"
anchor="$here/../skills/ponytail/anchor.txt"

# Predicates match the whole payload, not just user_input — the /ponytail token
# only realistically appears in the prompt. Full JSON parse only if this bites.
requests_deactivation() {
  local payload="$1"

  echo "$payload" | grep -qiE '/ponytail[[:space:]]+off|stop ponytail|normal mode'
}

requests_activation() {
  local payload="$1"

  # match the /ponytail command, not longer siblings like /ponytail-audit
  echo "$payload" | grep -qiE '/ponytail([^-A-Za-z0-9]|$)'
}

activate() {
  local marker="$1"

  mkdir -p "$(dirname "$marker")"
  touch "$marker"
  ponytail_skill_body "$skill"
}

payload="$(cat)"
marker="$(ponytail_marker_from_payload "$payload")" || exit 0

if requests_deactivation "$payload"; then
  rm -f "$marker"
elif requests_activation "$payload"; then
  activate "$marker"
elif [[ -f "$marker" ]]; then
  cat "$anchor"
fi
