#!/usr/bin/env bash

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$here/lib.sh"

skill="$here/../skills/ponytail/SKILL.md"

marker="$(ponytail_marker_from_payload "$(cat)")" || exit 0

# active session → reload the full ruleset (survives compact/resume); else silent
if [[ -f "$marker" ]]; then
  ponytail_skill_body "$skill"
fi
