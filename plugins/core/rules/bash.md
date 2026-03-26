---
paths:
  - "**/*.sh"
---

# Bash Script Conventions

## Shebang and Strict Mode

- `#!/usr/bin/env bash` for portability.
- `set -euo pipefail` on the line after shebang (separated by a blank line).
- Hooks that check exit codes intentionally may omit `set -e`.

## Naming

- Functions and variables: `snake_case`.
- Constants and exported env vars: `UPPER_SNAKE_CASE`.

## Functions

- Declare local variables with `local`; never leak into global scope.
- Use `readonly` for values that must not change.
- Return data via stdout; capture with `$(fn)`. Do not use global variables for return values.

## Variables and Conditionals

- Always double-quote variable expansions and command substitutions: `"$var"`, `"${var}"`, `"$(cmd)"`, `"$@"`.
- Use `${var:-default}` for defaults, `${var:?error msg}` for required values.
- Use arrays for lists of values — do not split strings with IFS.
- Use `[[ ]]` instead of `[ ]`.
- Check command existence with `command -v cmd &> /dev/null`, not `which`.

## Output and Exit Codes

- Diagnostic/error messages go to stderr: `echo "error: ..." >&2`.
- Hook scripts use exit 0 (pass) and exit 2 (block). Do not use exit 1.

## Files and Paths

- Resolve script directory: `script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`.
- Temporary files: `tmp=$(mktemp)` with cleanup via `trap 'rm -f "$tmp"' SIGINT SIGTERM ERR EXIT`.

## ShellCheck

- All scripts must pass `shellcheck`. Formatting is auto-checked by the `check-bash.sh` PostToolUse hook.
- To suppress a check: `# shellcheck disable=SCxxxx` with a comment explaining why.
